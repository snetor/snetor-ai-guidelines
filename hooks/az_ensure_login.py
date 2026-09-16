"""Garantit une session `az` vivante — au demarrage, ET avant chaque commande `az`.

## Pourquoi ce hook existe

Le 2026-09-15, pendant la montee du fork Twenty, la session `az` a expire **deux fois en pleine
sequence** : `AADSTS70043`, duree de vie 7200 secondes imposee par le controle de frequence de
connexion de l'acces conditionnel. Chaque expiration a interrompu l'owner au milieu d'un
enchainement de commandes, et il a fallu tout reprendre.

La regle « la session `az` expire apres ~2 h, ecrire des scripts courts et reprenables » etait
ecrite depuis L41. Elle s'est repetee quand meme. Une lecon qu'on repete est une lecon qui demande
un mecanisme.

## Ce qui existait, et pourquoi ca ne suffisait pas

`~/.azure-claude/az-ensure-login.ps1`, pose le 2026-08-30, hors de tout depot. Deux defauts,
mesures le 2026-09-16 :

1. **Son repli ne pouvait pas fonctionner.** Il lit `~/.azure-claude/sp.env` pour y trouver
   `AZURE_CLIENT_ID` et `AZURE_TENANT_ID` — un fichier qui n'a jamais existe sur ce poste. Le
   certificat `sp-claude-code-dev.pem` etait bien la, l'identite non. Le script affichait donc
   « `az login` manuel requis » et sortait en 0, depuis six semaines, sans jamais dire ce qui
   manquait.
2. **Il ne se declenchait qu'au demarrage de session.** Or l'incident est une expiration **en
   cours** de sequence : au demarrage, le jeton etait vivant les deux fois.

## Les trois proprietes de celui-ci

1. **Silencieux au vert, et gratuit.** Le demarrage d'`az` coute plus d'une seconde sur ce poste :
   l'invoquer avant chaque commande doublerait la latence de chacune. Le hook lit donc une date
   d'expiration mise en cache dans `~/.azure-claude/.expiration-jeton`, et ne parle a `az` que
   quand cette date approche (marge de 5 minutes). Au vert, il ne fait rien et n'ecrit rien — un
   hook qui parle a chaque demarrage devient un bruit qu'on cesse de lire, le meme mecanisme qui a
   rendu `lessons.md` illisible a 3 000 lignes.
2. **Il ne se declenche que sur ce qui le concerne.** Une commande qui ne parle pas a `az` ne paie
   pas meme une lecture de fichier.
3. **Il ne bloque JAMAIS.** Sortie 0 en toute circonstance. Une session de lecture de code n'a pas
   besoin d'Azure, et un garde-fou qui empeche d'ouvrir une session est pire que le defaut qu'il
   previent.

## Ce qu'il attend du poste, et qui n'est pas versionne

`~/.azure-claude/` porte le secret, il reste donc hors de Git :

```
sp.env                     AZURE_CLIENT_ID=... et AZURE_TENANT_ID=... (une par ligne)
sp-claude-code-dev.pem     certificat + cle privee du service principal
```

Sans `sp.env`, le hook detecte toujours le jeton mort et le dit — en nommant le fichier qui
manque, ce que l'ancien script ne faisait pas.

Branche en `SessionStart` et en `PreToolUse` par `scripts/deploy-claude.ps1`.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

# Le dossier hors depot qui porte le certificat et l'identite du service principal.
DOSSIER = pathlib.Path(os.path.expanduser("~")) / ".azure-claude"
CACHE = DOSSIER / ".expiration-jeton"
CERTIFICAT = DOSSIER / "sp-claude-code-dev.pem"
CONFIG_SP = DOSSIER / "sp.env"

# Assez tot pour ne pas engager une sequence longue sur un jeton qui tombe, assez tard pour ne pas
# interroger `az` a tout bout de champ.
MARGE = dt.timedelta(minutes=5)

# `az` comme COMMANDE, pas comme morceau de mot : precede d'un debut de ligne ou d'un separateur
# de shell, suivi d'une espace. Sans quoi `echo 'azure'` ou `ls /mnt/az` paieraient le controle.
_COMMANDE_AZ = re.compile(r"(?:^|[\s;&|(=])az(?:\.cmd)?(?=\s)", re.MULTILINE)

_OUTILS_SHELL = ("Bash", "PowerShell")


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
        pass  # un cache qu'on n'arrive pas a ecrire coute une interrogation de plus, rien d'autre


def _interroger_az() -> dt.datetime | None:
    """Rend la date d'expiration du jeton, ou `None` si la session est morte.

    ⚠️ `az account show` ne convient PAS : il lit le cache local et **reussit encore** quand la
    session est morte. Seul `az account get-access-token` force l'acquisition, donc echoue
    vraiment. Le commentaire etait deja dans le script PowerShell d'origine, il reste vrai.
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
    """`expires_on` est un epoch UTC ; `expiresOn` une heure LOCALE sans fuseau. Preferer le premier.

    Les deux coexistent selon la version d'`az`. Lire `expiresOn` comme de l'UTC decalerait la date
    du fuseau du poste — deux heures en ete a Paris, soit un cache qui se croit valide alors que le
    jeton est deja mort.
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


def _config_sp() -> dict[str, str] | None:
    """Lit `sp.env`. Rend `None` si le fichier manque ou n'a pas les deux cles attendues."""
    if not CONFIG_SP.is_file():
        return None
    valeurs: dict[str, str] = {}
    try:
        for ligne in CONFIG_SP.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*([A-Z_]+)\s*=\s*(.+?)\s*$", ligne)
            if m:
                valeurs[m.group(1)] = m.group(2)
    except OSError:
        return None
    if not valeurs.get("AZURE_CLIENT_ID") or not valeurs.get("AZURE_TENANT_ID"):
        return None
    return valeurs


def _reconnecter(config: dict[str, str]) -> bool:
    if not CERTIFICAT.is_file():
        return False
    try:
        sortie = subprocess.run(
            ["az", "login", "--service-principal",
             "--username", config["AZURE_CLIENT_ID"],
             "--tenant", config["AZURE_TENANT_ID"],
             "--certificate", str(CERTIFICAT), "-o", "none"],
            capture_output=True, text=True, timeout=120, shell=(os.name == "nt"),
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return sortie.returncode == 0


def _manque() -> str:
    """Nomme ce qui empeche le repli automatique, plutot que de dire « echec »."""
    if not CONFIG_SP.is_file():
        return f"`{CONFIG_SP.name}` absent (AZURE_CLIENT_ID / AZURE_TENANT_ID)"
    if not CERTIFICAT.is_file():
        return f"`{CERTIFICAT.name}` absent"
    return f"`{CONFIG_SP.name}` incomplet (AZURE_CLIENT_ID / AZURE_TENANT_ID)"


def traiter(evenement: dict) -> int:
    """Le coeur, separe de `main` pour etre testable sans passer par stdin."""
    if evenement.get("hook_event_name") != "SessionStart":
        if evenement.get("tool_name") not in _OUTILS_SHELL:
            return 0
        commande = (evenement.get("tool_input") or {}).get("command", "")
        if not _concerne_az(commande):
            return 0

    expiration = _expiration_en_cache()
    if expiration and expiration - MARGE > dt.datetime.now(dt.timezone.utc):
        return 0

    expiration = _interroger_az()
    if expiration:
        _ecrire_cache(expiration)
        return 0

    config = _config_sp()
    if config and _reconnecter(config):
        expiration = _interroger_az()
        if expiration:
            _ecrire_cache(expiration)
        print("az : session expiree, reconnectee via le service principal sp-claude-code-dev")
        return 0

    print(
        "az : session expiree (AADSTS70043, duree de vie 7200 s) et repli automatique "
        f"indisponible — {_manque()}.\n"
        "Lancer `az login` avant d'engager une sequence longue : le 2026-09-15, deux expirations "
        "en pleine montee ont coute une reprise complete."
    )
    return 0


def main() -> int:
    try:
        evenement = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError):
        return 0  # un hook qui casse la session est pire que le defaut qu'il previent
    try:
        return traiter(evenement)
    except Exception:  # noqa: BLE001 — aucune panne de ce hook ne doit empecher de travailler
        return 0


if __name__ == "__main__":
    sys.exit(main())
