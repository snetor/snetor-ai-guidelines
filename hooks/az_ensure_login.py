"""Prévient qu'une session `az` est morte — au démarrage, ET avant chaque commande `az`.

## Pourquoi ce hook existe

Le 2026-09-15, pendant la montée du fork Twenty, la session `az` a expiré **deux fois en pleine
séquence** : `AADSTS70043`, durée de vie 7200 secondes imposée par le contrôle de fréquence de
connexion de l'accès conditionnel. Chaque expiration a interrompu l'owner au milieu d'un
enchaînement de commandes, et il a fallu tout reprendre.

La règle « la session `az` expire après ~2 h, écrire des scripts courts et reprenables » était
écrite depuis L41. Elle s'est répétée quand même. Une leçon qu'on répète est une leçon qui demande
un mécanisme.

## Ce qui existait, et pourquoi ça ne suffisait pas

`~/.azure-claude/az-ensure-login.ps1`, posé le 2026-08-30, hors de tout dépôt. Trois défauts,
mesurés le 2026-09-16 :

1. **Il ne se déclenchait qu'au démarrage de session.** Or l'incident est une expiration **en
   cours** : les deux fois, le jeton était vivant au démarrage. C'est le défaut principal, et c'est
   celui que ce hook corrige.
2. **Il n'était ni versionné, ni déployé, ni testable.** Il mourait avec le poste — ce que la
   doctrine reproche justement à `memory/`.
3. **Son repli automatique ne pouvait pas fonctionner**, et personne ne le savait. Voir ci-dessous.

## Le repli par service principal : instruit, puis abandonné

Le script d'origine prétendait se reconnecter seul via un service principal à certificat. Il lisait
`~/.azure-claude/sp.env` pour y trouver `AZURE_CLIENT_ID` et `AZURE_TENANT_ID` — un fichier qui n'a
jamais existé. Le certificat `sp-claude-code-dev.pem` était bien là, l'identité non.

**Vérifié dans Entra le 2026-09-17, de trois façons :** aucun service principal ni application
nommés `sp-claude-*`, rien dans les `deletedItems` récupérables, et l'empreinte du certificat
(`06:FB:61:86:…:D0:73`) ne figure dans les `keyCredentials` d'**aucune** des 141 app registrations
du tenant, dont 76 en portent au moins un. L'identité n'a jamais été créée.

**Décision du 2026-09-17 : on ne la crée pas**, et le repli automatique est retiré de ce hook.

Le motif est écrit dans `azure-landing-zone/CLAUDE.md` : *« Ne pas chercher à leur créer un secret
pour "débloquer" un usage local — Entra refusera, et c'est voulu. Pour un accès local, `az login`
interactif. »* Et l'audit `docs/dated/security-audit-ia-2026-09-14.md` classe 🟢 SOLIDE le fait que
les identités de CI n'aient **aucun credential**, 🟠 FRAGILE les applications daemon qui portent des
secrets longs.

Le fond, en une phrase : la session `az` dure deux heures parce qu'une politique d'accès
conditionnel l'a décidé. Un certificat posé sur le poste aurait ouvert la même porte **jusqu'en
2027** — il aurait supprimé précisément l'écart que cette fenêtre existe pour créer.

Ce hook fait donc ce qu'il peut faire sans rien affaiblir : **il prévient au bon moment**.

## Les trois propriétés

1. **Silencieux au vert, et gratuit.** Le démarrage d'`az` coûte plus d'une seconde sur ce poste :
   l'invoquer avant chaque commande doublerait la latence de chacune. Le hook lit donc une date
   d'expiration mise en cache dans `~/.azure-claude/.expiration-jeton`, et ne parle à `az` que
   quand cette date approche (marge de 5 minutes). Au vert, il ne fait rien et n'écrit rien — un
   hook qui parle à chaque démarrage devient un bruit qu'on cesse de lire, le même mécanisme qui a
   rendu `lessons.md` illisible à 3 000 lignes.
2. **Il ne se déclenche que sur ce qui le concerne.** Une commande qui ne parle pas à `az` ne paie
   pas même une lecture de fichier.
3. **Il ne bloque JAMAIS.** Sortie 0 en toute circonstance. Une session de lecture de code n'a pas
   besoin d'Azure, et un garde-fou qui empêche d'ouvrir une session est pire que le défaut qu'il
   prévient.

Branché en `SessionStart` et en `PreToolUse` par `scripts/deploy-claude.ps1`.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

# Un seul fichier, et il ne porte aucun secret : la date d'expiration du jeton courant.
DOSSIER = pathlib.Path(os.path.expanduser("~")) / ".azure-claude"
CACHE = DOSSIER / ".expiration-jeton"

# Assez tôt pour ne pas engager une séquence longue sur un jeton qui tombe, assez tard pour ne pas
# interroger `az` à tout bout de champ.
MARGE = dt.timedelta(minutes=5)

# `az` comme COMMANDE, pas comme morceau de mot : précédé d'un début de ligne ou d'un séparateur de
# shell, suivi d'une espace. Sans quoi `echo 'azure'` ou `ls /mnt/az` paieraient le contrôle.
#
# ⚠️ Volontairement plus LARGE que la règle homonyme de `guard.py`, et l'asymétrie est réfléchie.
# Là-bas, un faux positif refuse un geste légitime et apprend à contourner le garde-fou : le motif
# doit donc être étroit. Ici, un faux positif coûte une lecture de fichier, et un faux négatif coûte
# l'incident du 2026-09-15. On accepte de vérifier trop souvent.
_COMMANDE_AZ = re.compile(r"(?:^|[\s;&|(=])az(?:\.cmd)?(?=\s)", re.MULTILINE)

_OUTILS_SHELL = ("Bash", "PowerShell")

MESSAGE = (
    "az : la session est expirée (AADSTS70043 — durée de vie 7200 s, imposée par le contrôle de "
    "fréquence de connexion).\n"
    "Faire : `az login`, avant d'engager une séquence longue. Le 2026-09-15, deux expirations en "
    "pleine montée du fork Twenty ont coûté une reprise complète.\n"
    "Il n'y a pas de reconnexion automatique, et c'est délibéré : un certificat sur le poste "
    "ouvrirait la même porte jusqu'en 2027, là où cette fenêtre de deux heures existe pour l'en "
    "empêcher (décision du 2026-09-17)."
)


def _concerne_az(commande: str) -> bool:
    return bool(_COMMANDE_AZ.search(commande or ""))


def _expiration_en_cache() -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(CACHE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _ecrire_cache(expiration: dt.datetime) -> None:
    try:
        DOSSIER.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(expiration.isoformat(), encoding="utf-8")
    except OSError:
        pass  # un cache qu'on n'arrive pas à écrire coûte une interrogation de plus, rien d'autre


def _interroger_az() -> dt.datetime | None:
    """Rend la date d'expiration du jeton, ou `None` si la session est morte.

    ⚠️ `az account show` ne convient PAS : il lit le cache local et **réussit encore** quand la
    session est morte. Seul `az account get-access-token` force l'acquisition, donc échoue vraiment.
    Le commentaire était déjà dans le script PowerShell d'origine, il reste vrai.
    """
    try:
        sortie = subprocess.run(
            ["az", "account", "get-access-token", "-o", "json"],
            capture_output=True, text=True, timeout=60, shell=(os.name == "nt"),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if sortie.returncode != 0:
        return None
    try:
        charge = json.loads(sortie.stdout)
    except (json.JSONDecodeError, ValueError):
        return None
    return _expiration(charge)


def _expiration(charge: dict) -> dt.datetime | None:
    """`expires_on` est un epoch UTC ; `expiresOn` une heure LOCALE sans fuseau. Préférer le premier.

    Les deux coexistent selon la version d'`az`. Lire `expiresOn` comme de l'UTC décalerait la date
    du fuseau du poste — deux heures en été à Paris, soit un cache qui se croit valide alors que le
    jeton est déjà mort.
    """
    epoch = charge.get("expires_on")
    if isinstance(epoch, (int, float)):
        return dt.datetime.fromtimestamp(epoch, dt.timezone.utc)
    brut = charge.get("expiresOn")
    if isinstance(brut, str):
        try:
            return dt.datetime.fromisoformat(brut).astimezone(dt.timezone.utc)
        except ValueError:
            return None
    return None


def traiter(evenement: dict) -> int:
    """Le cœur, séparé de `main` pour être testable sans passer par stdin."""
    if evenement.get("hook_event_name") != "SessionStart":
        if evenement.get("tool_name") not in _OUTILS_SHELL:
            return 0
        if not _concerne_az((evenement.get("tool_input") or {}).get("command", "")):
            return 0

    expiration = _expiration_en_cache()
    if expiration and expiration - MARGE > dt.datetime.now(dt.timezone.utc):
        return 0

    expiration = _interroger_az()
    if expiration:
        _ecrire_cache(expiration)
        return 0

    print(MESSAGE)
    return 0


def main() -> int:
    try:
        evenement = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError):
        return 0  # un hook qui casse la session est pire que le défaut qu'il prévient
    try:
        return traiter(evenement)
    except Exception:  # noqa: BLE001 — aucune panne de ce hook ne doit empêcher de travailler
        return 0


if __name__ == "__main__":
    sys.exit(main())
