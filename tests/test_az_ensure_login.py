"""Le controle de session `az` : silencieux au vert, gratuit quand il vient de verifier.

Deux incidents le justifient, et ils ne disent pas la meme chose.

**Le 2026-09-15**, pendant la montee du fork Twenty, la session `az` a expire DEUX FOIS en pleine
sequence (`AADSTS70043`, duree de vie 7200 s imposee par le controle de frequence de connexion).
L'owner a ete interrompu chaque fois. La regle existait pourtant depuis L41 : c'est une recidive,
et une recidive demande un mecanisme, pas une phrase de plus.

**Le 2026-09-16**, en instruisant la mesure, le controle existant s'est revele decoratif :
`~/.azure-claude/az-ensure-login.ps1` detecte bien le jeton mort, mais son repli service principal
lit `~/.azure-claude/sp.env`, un fichier qui N'A JAMAIS EXISTE sur ce poste. Il affichait donc
« `az login` manuel requis » et sortait en 0 — depuis le 2026-08-30. De plus il ne se declenchait
qu'au demarrage de session, alors que l'incident est une expiration EN COURS de sequence.

**Le 2026-09-17**, le repli lui-meme a ete instruit puis ABANDONNE. L identite `sp-claude-code-dev`
n existait dans Entra sous aucune forme, et la creer aurait remplace une cle qui se perime toutes
les deux heures par une cle valable jusqu en 2027, posee en clair sur le poste. C est exactement
l ecart que le controle de frequence de connexion existe pour supprimer, et
`azure-landing-zone/CLAUDE.md` avait deja tranche : « Pour un acces local, `az login` interactif. »
Ce hook previent donc au bon moment, et ne repare rien — deux tests epinglent le fait que ni le
message ni le code ne promettent le contraire.

D'ou les trois proprietes que cette suite epingle :

1. **Silencieux au vert, et GRATUIT.** Un hook qui lance `az` avant chaque commande double la
   latence de chacune (le demarrage d'`az` coute plus d'une seconde sur ce poste). Le controle lit
   donc une date d'expiration en cache et ne parle a `az` que quand elle approche.
2. **Il ne se declenche que sur ce qui le concerne.** Une commande qui ne parle pas a `az` ne paie
   rien du tout, pas meme une lecture de fichier.
3. **Il ne bloque JAMAIS.** Sortie 0 en toute circonstance : une session de lecture de code n'a pas
   besoin d'Azure, et un garde-fou qui empeche d'ouvrir une session est pire que le defaut qu'il
   previent.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

import az_ensure_login as hook  # `tests/conftest.py` met `hooks/` sur le chemin


def _dans(**delta) -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(**delta)


@pytest.fixture
def sans_az(monkeypatch):
    """Toute invocation reelle d'`az` fait echouer le test : on veut prouver qu'elle n'a pas lieu."""
    def interdit(*_a, **_k):
        raise AssertionError("`az` a ete invoque alors que le cache devait suffire")
    monkeypatch.setattr(hook, "_interroger_az", interdit)


def _evenement(**champs) -> str:
    base = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "az group list"}}
    base.update(champs)
    return json.dumps(base)


# --- ce qui ne doit rien couter -------------------------------------------------------------

def test_silencieux_et_gratuit_quand_le_cache_est_frais(monkeypatch, capsys, sans_az):
    monkeypatch.setattr(hook, "_expiration_en_cache", lambda: _dans(hours=1))
    assert hook.traiter(json.loads(_evenement())) == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "commande",
    [
        "pytest -q",
        "git commit -F message.txt",
        "gh pr checks 36 --json name,state",
        "python scripts/check_docs.py --repo-root .",
        "echo 'azure'",          # `azure` n'est pas la commande `az`
        "ls /mnt/az",            # `az` en fin de chemin
    ],
)
def test_une_commande_sans_az_ne_coute_rien(commande, monkeypatch, sans_az):
    """Pas meme une lecture de cache : le hook sort avant d'y toucher."""
    def interdit():
        raise AssertionError("le cache a ete lu pour une commande sans `az`")
    monkeypatch.setattr(hook, "_expiration_en_cache", interdit)
    assert hook.traiter(json.loads(_evenement(tool_input={"command": commande}))) == 0


@pytest.mark.parametrize(
    "commande",
    [
        "az group list",
        'cd "C:/Users/x/depot" && az containerapp job start -n caj-x',
        "& az account show",
        "az.cmd account show",
        "terraform plan; az account show",
    ],
)
def test_une_commande_avec_az_est_bien_reconnue(commande):
    assert hook._concerne_az(commande), f"non reconnue : {commande}"


def test_un_outil_qui_n_est_pas_un_shell_ne_declenche_rien(monkeypatch, sans_az):
    def interdit():
        raise AssertionError("le cache a ete lu pour un outil sans commande")
    monkeypatch.setattr(hook, "_expiration_en_cache", interdit)
    evenement = {"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_input": {"file_path": "az.md"}}
    assert hook.traiter(evenement) == 0


# --- ce qui doit declencher le controle ------------------------------------------------------

def test_le_demarrage_de_session_controle_toujours(monkeypatch, capsys):
    """Pas de commande a inspecter : `SessionStart` verifie sans condition."""
    appels = []
    monkeypatch.setattr(hook, "_expiration_en_cache", lambda: None)
    monkeypatch.setattr(hook, "_ecrire_cache", lambda _d: appels.append("cache"))
    monkeypatch.setattr(hook, "_interroger_az", lambda: _dans(hours=2))
    assert hook.traiter({"hook_event_name": "SessionStart"}) == 0
    assert appels == ["cache"], "l'expiration obtenue doit etre mise en cache"
    assert capsys.readouterr().out == "", "au vert, le hook se tait"


def test_un_cache_qui_expire_bientot_relance_la_verification(monkeypatch):
    """La marge evite de demarrer une sequence longue sur un jeton qui tombe dans cinq minutes."""
    appels = []
    monkeypatch.setattr(hook, "_expiration_en_cache", lambda: _dans(minutes=2))
    monkeypatch.setattr(hook, "_ecrire_cache", lambda _d: None)
    monkeypatch.setattr(hook, "_interroger_az", lambda: appels.append("az") or _dans(hours=2))
    assert hook.traiter(json.loads(_evenement())) == 0
    assert appels == ["az"]


# --- ce qui doit etre dit, et comment --------------------------------------------------------

def test_jeton_mort_previent_sans_promettre_de_repli(monkeypatch, capsys):
    """Le repli par service principal a ete instruit le 2026-09-17, puis ABANDONNE.

    L identite `sp-claude-code-dev` n existait pas dans Entra : ni service principal, ni
    application, rien dans les `deletedItems`, et l empreinte du certificat ne figurait dans
    AUCUNE des 141 app registrations du tenant. Le script PowerShell d origine promettait donc
    depuis six semaines une reconnexion qui ne pouvait pas avoir lieu.

    La creer aurait remplace une cle qui se perime toutes les deux heures par une cle valable
    jusqu en 2027, posee en clair sur le poste — exactement l ecart que le controle de frequence
    de connexion existe pour supprimer. `azure-landing-zone/CLAUDE.md` tranche deja :
    « Pour un acces local, `az login` interactif. »

    Ce test epingle la consequence : le message dit quoi faire, et ne promet rien d automatique.
    """
    monkeypatch.setattr(hook, "_expiration_en_cache", lambda: None)
    monkeypatch.setattr(hook, "_interroger_az", lambda: None)
    assert hook.traiter({"hook_event_name": "SessionStart"}) == 0
    sortie = capsys.readouterr().out
    assert "az login" in sortie
    assert "AADSTS70043" in sortie, "le motif doit nommer l erreur qu on verra vraiment"
    for promesse in ("sp.env", "service principal sp-claude", "reconnecte"):
        assert promesse not in sortie, (
            f"le message promet encore un repli automatique ({promesse!r}) : il n existe pas, "
            "et l avoir cru a coute six semaines de fausse securite"
        )


def test_le_repli_par_service_principal_n_est_plus_dans_le_code(monkeypatch):
    """Du code mort qui a l air d un filet de securite est pire que pas de filet."""
    for disparu in ("_config_sp", "_reconnecter", "_manque", "CERTIFICAT", "CONFIG_SP"):
        assert not hasattr(hook, disparu), (
            f"`{disparu}` survit au retrait du repli : soit il sert, soit il ment."
        )


# --- ce qui ne doit jamais arriver -----------------------------------------------------------

def test_un_evenement_illisible_ne_casse_pas_la_session(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _FauxStdin("pas du json"))
    assert hook.main() == 0
    assert capsys.readouterr().out == ""


def test_une_exception_inattendue_ne_casse_pas_la_session(monkeypatch):
    """Perdre le controle du jeton est ennuyeux ; ne pas pouvoir ouvrir une session ne l'est pas
    de la meme facon."""
    def explose():
        raise RuntimeError("disque plein")
    monkeypatch.setattr(hook, "_expiration_en_cache", explose)
    monkeypatch.setattr("sys.stdin", _FauxStdin(_evenement()))
    assert hook.main() == 0


class _FauxStdin:
    def __init__(self, contenu: str) -> None:
        self._contenu = contenu

    def read(self) -> str:
        return self._contenu
