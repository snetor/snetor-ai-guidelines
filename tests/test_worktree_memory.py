"""La memoire du depot principal suit dans ses worktrees — et rien d'autre ne bouge.

Ce hook touche au dossier `memory/` de l'utilisateur, qui n'est ni versionne ni sauvegarde. Les
tests qui comptent le plus ne sont donc pas ceux du chemin nominal, mais les trois refus : ne pas
deviner une convention de nommage, ne pas ecraser une memoire existante, ne pas bloquer une
session. Chacun a son test ci-dessous.
"""

from __future__ import annotations

import io
import json
import os
import pathlib
import subprocess

import pytest

import worktree_memory  # `tests/conftest.py` met `hooks/` sur le chemin


# --- le nom de dossier d'un projet ----------------------------------------------------------

@pytest.mark.parametrize(
    "chemin, attendu",
    [
        (
            r"C:\Users\c.peponnet\Dev-projects\pro\snetor-pim",
            "C--Users-c-peponnet-Dev-projects-pro-snetor-pim",
        ),
        (
            r"C:\Users\c.peponnet\Dev-projects\pro\snetor-pim\.claude\worktrees\catalogue-cartes",
            "C--Users-c-peponnet-Dev-projects-pro-snetor-pim--claude-worktrees-catalogue-cartes",
        ),
        ("/home/moi/dev/snetor-pim", "-home-moi-dev-snetor-pim"),
    ],
)
def test_le_slug_reproduit_les_noms_reellement_observes(chemin, attendu):
    """Paires relevees dans `~/.claude/projects/` le 2026-09-14."""
    assert worktree_memory.slug_projet(chemin) == attendu


# --- refus n.1 : ne pas deviner -------------------------------------------------------------

def test_la_convention_est_confirmee_par_le_transcript():
    cwd = r"C:\Users\moi\depot"
    transcript = r"C:\Users\moi\.claude\projects\C--Users-moi-depot\abc.jsonl"
    assert worktree_memory.convention_verifiee(cwd, transcript) is True


def test_une_convention_de_nommage_differente_est_refusee():
    """Si Claude Code changeait sa convention, le hook doit se desarmer, pas se tromper de cible."""
    cwd = r"C:\Users\moi\depot"
    transcript = r"C:\Users\moi\.claude\projects\un-hash-opaque-42\abc.jsonl"
    assert worktree_memory.convention_verifiee(cwd, transcript) is False


def test_un_transcript_absent_refuse_la_verification():
    assert worktree_memory.convention_verifiee(r"C:\x", "") is False


# --- reconnaissance d'un worktree -----------------------------------------------------------

def _depot_git(racine: pathlib.Path) -> None:
    racine.mkdir(parents=True, exist_ok=True)
    lance = lambda *args: subprocess.run(args, cwd=racine, capture_output=True, check=True)
    lance("git", "init", "-q", "-b", "main")
    lance("git", "config", "user.email", "test@example.invalid")
    lance("git", "config", "user.name", "Test")
    (racine / "fichier.txt").write_text("contenu", encoding="utf-8")
    lance("git", "add", "-A")
    lance("git", "commit", "-qm", "initial")


def test_un_checkout_ordinaire_n_est_pas_un_worktree(tmp_path):
    racine = tmp_path / "depot"
    _depot_git(racine)
    assert worktree_memory.depot_principal(str(racine)) is None


def test_un_worktree_lie_renvoie_la_racine_du_depot_principal(tmp_path):
    racine = tmp_path / "depot"
    _depot_git(racine)
    worktree = racine / ".claude" / "worktrees" / "chantier"
    subprocess.run(
        ["git", "worktree", "add", "-q", str(worktree), "-b", "feat/x"],
        cwd=racine,
        capture_output=True,
        check=True,
    )
    trouve = worktree_memory.depot_principal(str(worktree))
    assert trouve is not None
    assert pathlib.Path(trouve).resolve() == racine.resolve()


def test_un_dossier_hors_git_ne_casse_rien(tmp_path):
    assert worktree_memory.depot_principal(str(tmp_path)) is None


# --- bout en bout ---------------------------------------------------------------------------

@pytest.fixture
def scene(tmp_path, monkeypatch):
    """Un depot, son worktree, et l'arborescence `projects/` correspondante."""
    racine = tmp_path / "depot"
    _depot_git(racine)
    worktree = racine / ".claude" / "worktrees" / "chantier"
    subprocess.run(
        ["git", "worktree", "add", "-q", str(worktree), "-b", "feat/x"],
        cwd=racine,
        capture_output=True,
        check=True,
    )

    projets = tmp_path / "projects"
    memoire_principale = projets / worktree_memory.slug_projet(str(racine)) / "memory"
    memoire_principale.mkdir(parents=True)
    (memoire_principale / "MEMORY.md").write_text("# index", encoding="utf-8")

    slug_worktree = worktree_memory.slug_projet(str(worktree))
    transcript = projets / slug_worktree / "session.jsonl"
    transcript.parent.mkdir(parents=True)

    class Scene:
        pass

    scene = Scene()
    scene.racine, scene.worktree = racine, worktree
    scene.memoire_principale = memoire_principale
    scene.memoire_worktree = projets / slug_worktree / "memory"
    scene.charge = {"cwd": str(worktree), "transcript_path": str(transcript)}
    return scene


def _lancer(charge, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(charge)))
    code = worktree_memory.main()
    return code, capsys.readouterr().out


def test_la_memoire_du_depot_principal_devient_lisible_depuis_le_worktree(
    scene, monkeypatch, capsys
):
    code, sortie = _lancer(scene.charge, monkeypatch, capsys)
    assert code == 0
    assert (scene.memoire_worktree / "MEMORY.md").read_text(encoding="utf-8") == "# index"
    assert "reliee" in sortie or "reli" in sortie


def test_une_lecon_ecrite_en_worktree_survit_au_worktree(scene, monkeypatch, capsys):
    """Le sens de l'operation : l'ecriture tombe cote depot principal, pas dans le lien."""
    _lancer(scene.charge, monkeypatch, capsys)
    (scene.memoire_worktree / "lecon.md").write_text("apprise en worktree", encoding="utf-8")
    assert (scene.memoire_principale / "lecon.md").read_text(encoding="utf-8") == (
        "apprise en worktree"
    )


def test_relancer_le_hook_ne_change_rien(scene, monkeypatch, capsys):
    _lancer(scene.charge, monkeypatch, capsys)
    code, sortie = _lancer(scene.charge, monkeypatch, capsys)
    assert code == 0
    assert sortie.strip() == "", "la deuxieme session ne doit produire aucun bruit"


# --- refus n.2 : ne pas ecraser -------------------------------------------------------------

def test_une_memoire_de_worktree_non_vide_est_laissee_intacte(scene, monkeypatch, capsys):
    scene.memoire_worktree.mkdir(parents=True)
    (scene.memoire_worktree / "deja-la.md").write_text("a ne pas perdre", encoding="utf-8")

    code, sortie = _lancer(scene.charge, monkeypatch, capsys)

    assert code == 0
    assert (scene.memoire_worktree / "deja-la.md").read_text(encoding="utf-8") == "a ne pas perdre"
    assert not scene.memoire_worktree.is_symlink()
    assert "isol" in sortie, "le cas doit etre signale, pas tu"


def test_un_depot_principal_sans_memoire_ne_declenche_rien(scene, monkeypatch, capsys):
    for enfant in scene.memoire_principale.iterdir():
        enfant.unlink()
    scene.memoire_principale.rmdir()

    code, sortie = _lancer(scene.charge, monkeypatch, capsys)

    assert code == 0
    assert not scene.memoire_worktree.exists()
    assert sortie.strip() == ""


def test_un_checkout_ordinaire_ne_declenche_rien(scene, monkeypatch, capsys):
    charge = dict(scene.charge, cwd=str(scene.racine))
    code, sortie = _lancer(charge, monkeypatch, capsys)
    assert code == 0
    assert sortie.strip() == ""


def test_une_convention_inconnue_ne_declenche_rien(scene, monkeypatch, capsys):
    charge = dict(scene.charge, transcript_path=str(scene.racine / "ailleurs" / "s.jsonl"))
    code, sortie = _lancer(charge, monkeypatch, capsys)
    assert code == 0
    assert not scene.memoire_worktree.exists()


# --- refus n.3 : ne jamais bloquer une session ----------------------------------------------

@pytest.mark.parametrize("entree", ["", "pas du json", "null", "[]", "{}"])
def test_une_entree_illisible_laisse_la_session_demarrer(entree, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(entree))
    assert worktree_memory.main() == 0


def test_un_git_absent_laisse_la_session_demarrer(scene, monkeypatch, capsys):
    def git_introuvable(*_args, **_kwargs):
        raise OSError("git absent")

    monkeypatch.setattr(subprocess, "run", git_introuvable)
    code, _ = _lancer(scene.charge, monkeypatch, capsys)
    assert code == 0
