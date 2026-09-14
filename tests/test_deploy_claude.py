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
