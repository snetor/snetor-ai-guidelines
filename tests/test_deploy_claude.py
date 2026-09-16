"""Le deployeur ne peut pas mourir sur la sortie normale d'un executable.

Une seule regle ici, et elle vient d'un incident : le 2026-09-14, la phase 5 de
`deploy-claude.ps1` echouait sur sa toute premiere action depuis des semaines, sans que
personne ne le sache. Le poste de l'auteur du depot tournait sans `workflow.md` ni
`snetor-guidelines.md`, avec un `CLAUDE.md` portant une copie collee a la main.

Le mecanisme, en une phrase : `git clone` ecrit son « Cloning into 'x'... » sur **stderr** meme
quand tout va bien ; en PowerShell 5.1, `2>&1` emballe chaque ligne de stderr dans un
ErrorRecord ; et `$ErrorActionPreference = 'Stop'`, pose en tete du script, rend cet ErrorRecord
terminant. Le `try/catch` de l'execution principale affichait « Phase 5 echouee » et passait a la
suite — rien n'etait copie, et le deploiement se declarait termine.

Cette classe de defaut est invisible a la relecture : la ligne fautive ressemble a une ligne qui
fait taire du bruit. Elle se verifie par un programme, donc elle ne reste pas en prose.
"""

from __future__ import annotations

import pathlib
import re

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "deploy-claude.ps1"


@pytest.fixture(scope="module")
def source() -> str:
    return SCRIPT.read_text(encoding="utf-8-sig")


def test_le_deployeur_existe(source):
    assert source.strip(), f"{SCRIPT} introuvable ou vide"


def test_le_script_s_arrete_a_la_premiere_erreur(source):
    """Premisse de la regle suivante. Si ce reglage disparait, la regle doit etre revue."""
    assert re.search(r"^\$ErrorActionPreference\s*=\s*'Stop'", source, re.MULTILINE), (
        "`$ErrorActionPreference = 'Stop'` a disparu : la regle sur `2>&1` ci-dessous "
        "reposait dessus, la reexaminer avant de la relacher."
    )


def test_aucune_redirection_de_stderr_sur_un_executable_natif(source):
    """`2>&1` + ErrorActionPreference Stop = le script meurt sur un message de progression.

    Pour faire taire un executable, utiliser son propre drapeau (`--quiet`, `--silent`, `-q`)
    et lire `$LASTEXITCODE`, jamais une redirection PowerShell.
    """
    fautives = [
        f"{numero}: {ligne.strip()}"
        for numero, ligne in enumerate(source.splitlines(), start=1)
        if "2>&1" in ligne and not ligne.strip().startswith("#")
    ]
    assert not fautives, (
        "Redirection de stderr sur un executable natif — en PowerShell 5.1 chaque ligne de "
        "stderr devient un ErrorRecord, terminant sous `ErrorActionPreference = 'Stop'` :\n  "
        + "\n  ".join(fautives)
    )


def test_le_clone_lit_son_code_de_retour(source):
    """Ne pas rediriger ne suffit pas : encore faut-il savoir si le clone a reussi."""
    bloc = re.search(r"&\s*git\s+clone[^\n]*\n(?:[^\n]*\n){0,4}", source)
    assert bloc, "appel a `git clone` introuvable dans le deployeur"
    assert "$LASTEXITCODE" in bloc.group(0), (
        "`git clone` ne verifie pas `$LASTEXITCODE` : un clone echoue passerait pour un succes "
        "jusqu'au `Test-Path` suivant, avec un message sans rapport."
    )


def test_le_deployeur_impose_nx_daemon_false(source):
    """Le daemon Nx bloque le build sans ecrire un log : la variable qui le coupe est deployee.

    Incident du 2026-09-14, montee du fork Twenty `twenty/v2.30.0` -> `twenty/v2.39.0` :
    `nx build twenty-shared` est reste bloque 11 heures sur son etape `generateBarrels`, sans
    ecrire une ligne de log ni consommer de CPU. Un blocage silencieux qui ressemble a une
    lenteur, donc qu'on attend au lieu de le diagnostiquer. `NX_DAEMON=false` le debloque.

    La variable est posee au niveau utilisateur, et non dans le fork : le
    `.claude/settings.json` de `snetor/twenty` est un fichier AMONT — identique a
    `upstream/main`, et reecrit 5 fois en 6 mois par Twenty. Y ecrire la variable fabriquerait
    un point d'ancrage de plus a recoller a chaque montee.
    """
    bloc = re.search(r"\$snetorEnv\s*=\s*\[ordered\]@\{(.*?)^\s*\}", source, re.DOTALL | re.MULTILINE)
    assert bloc, "bloc `$snetorEnv` introuvable dans le deployeur"
    assert re.search(r"NX_DAEMON\s*=\s*'false'", bloc.group(1)), (
        "`NX_DAEMON = 'false'` absent de `$snetorEnv` : sans lui, un `nx build` peut rester "
        "bloque indefiniment sur son daemon, sans un log pour le dire."
    )


def test_les_variables_d_environnement_sont_fusionnees_une_a_une(source):
    """Remplacer le bloc `env` entier effacerait les variables deja posees sur le poste.

    Le settings utilisateur en porte d'autres (`MAX_THINKING_TOKENS` au 2026-09-16). Le
    deployeur tourne en fusion, pas en reinitialisation : chaque cle s'ajoute avec `-Force`,
    l'objet `env` ne se reassigne jamais en bloc.
    """
    assert re.search(
        r"foreach\s*\(\$k\s+in\s+\$snetorEnv\.Keys\)[^\n]*\n\s*\$cfg\.env\s*\|\s*Add-Member[^\n]*-Force",
        source,
    ), (
        "les cles de `$snetorEnv` ne sont pas ajoutees une a une avec `-Force` sur `$cfg.env` : "
        "une reassignation en bloc effacerait les variables deja posees sur le poste."
    )
