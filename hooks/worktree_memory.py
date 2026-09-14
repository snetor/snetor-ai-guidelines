"""Rend la mémoire du dépôt principal visible depuis ses worktrees.

Le problème, en une phrase : Claude Code range la mémoire d'un projet dans un dossier dont le nom
est le **chemin** du répertoire de travail. Un worktree est le même dépôt dans un autre chemin —
donc un autre dossier, vide. `CLAUDE.md` suit (il est versionné, il voyage avec la branche), la
mémoire non.

Mesuré le 2026-09-14 sur `snetor-pim` : 52 fichiers de mémoire côté checkout principal, **0** dans
les trois projets worktree, qui totalisaient pourtant 8 sessions. Or le standard Snetor impose de
travailler en worktree (`snetor-guidelines.md`, Git Hygiene) : la règle désarmait la mémoire à
chaque chantier sérieux.

Ce hook relie `projects/<slug-du-worktree>/memory` à `projects/<slug-du-dépôt-principal>/memory`
par une jonction de répertoire (Windows) ou un lien symbolique (POSIX). Lecture **et** écriture
tombent alors dans la mémoire du dépôt principal : une leçon apprise en worktree survit au
`git worktree remove`.

Branché en `SessionStart` par `scripts/deploy-claude.ps1`.

Trois refus de principe, parce qu'un garde-fou qui se trompe est un garde-fou qu'on débranche :

1. **Il ne devine jamais.** Le nom de dossier d'un projet est une convention interne de Claude
   Code, pas un contrat. Le hook la déduit, puis la **vérifie** contre `transcript_path`, que
   Claude Code lui fournit et qui contient le vrai nom. Si la vérification échoue — convention
   changée — il ne fait rien.
2. **Il n'écrase jamais une mémoire existante.** Un dossier `memory/` non vide côté worktree est
   laissé intact et signalé, jamais remplacé par un lien.
3. **Il ne bloque jamais une session.** Toute erreur inattendue sort en code 0. Perdre la mémoire
   partagée est ennuyeux ; ne pas pouvoir ouvrir une session ne l'est pas de la même façon.
"""

import json
import os
import pathlib
import re
import subprocess
import sys


def slug_projet(chemin: str) -> str:
    """Nom du dossier sous `~/.claude/projects/` pour un répertoire de travail donné.

    Convention observée : tout caractère non alphanumérique devient un tiret. `C:\\Users\\c.x\\p`
    donne `C--Users-c-x-p`. Jamais utilisée sans la validation de `convention_verifiee()`.
    """
    return re.sub(r"[^a-zA-Z0-9]", "-", chemin)


def convention_verifiee(cwd: str, transcript_path: str) -> bool:
    """Confirme que `slug_projet` reproduit bien le nom que Claude Code a réellement utilisé.

    `transcript_path` pointe vers `~/.claude/projects/<slug>/<session>.jsonl` : le nom du dossier
    parent EST la réponse. On compare plutôt que de faire confiance.
    """
    if not transcript_path:
        return False
    try:
        slug_reel = pathlib.Path(transcript_path).parent.name
    except (ValueError, OSError):
        return False
    return bool(slug_reel) and slug_reel == slug_projet(cwd)


def depot_principal(cwd: str) -> str | None:
    """Racine du dépôt principal si `cwd` est un worktree lié, sinon None.

    Repose sur git, pas sur l'emplacement du worktree : `--git-dir` et `--git-common-dir` diffèrent
    dans un worktree lié et coïncident dans un checkout ordinaire. Le standard Snetor range les
    worktrees sous `.claude/worktrees/`, mais rien n'y oblige — on ne teste pas le chemin.
    """
    try:
        resultat = subprocess.run(
            ["git", "rev-parse", "--git-dir", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if resultat.returncode != 0:
        return None

    lignes = [ligne.strip() for ligne in resultat.stdout.splitlines() if ligne.strip()]
    if len(lignes) != 2:
        return None

    git_dir, git_common_dir = (pathlib.Path(cwd) / ligne for ligne in lignes)
    try:
        git_dir, git_common_dir = git_dir.resolve(), git_common_dir.resolve()
    except OSError:
        return None

    if git_dir == git_common_dir:
        return None  # checkout ordinaire, rien à faire
    return str(git_common_dir.parent)


def creer_lien(lien: pathlib.Path, cible: pathlib.Path) -> bool:
    """Jonction de répertoire sous Windows, lien symbolique ailleurs.

    `mklink /J` plutôt que `os.symlink` sous Windows : la jonction ne demande ni droits
    administrateur ni mode développeur, là où le lien symbolique exige l'un des deux.
    """
    if os.name == "nt":
        try:
            resultat = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(lien), str(cible)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return resultat.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    try:
        os.symlink(str(cible), str(lien), target_is_directory=True)
        return True
    except OSError:
        return False


def contexte(message: str) -> None:
    """Émet une ligne de contexte pour la session, au format attendu d'un hook SessionStart."""
    sortie = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    print(json.dumps(sortie, ensure_ascii=False))


def main() -> int:
    try:
        charge = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(charge, dict):
        return 0  # `null` et `[]` sont du JSON valide, et n'ont pas de `.get`

    cwd = charge.get("cwd") or ""
    transcript_path = charge.get("transcript_path") or ""
    if not cwd:
        return 0

    racine_principale = depot_principal(cwd)
    if racine_principale is None:
        return 0  # pas un worktree

    if not convention_verifiee(cwd, transcript_path):
        return 0  # convention de nommage inconnue : on ne devine pas

    projets = pathlib.Path(transcript_path).parent.parent
    memoire_principale = projets / slug_projet(racine_principale) / "memory"
    if not memoire_principale.is_dir():
        return 0  # le dépôt principal n'a pas de mémoire à partager

    memoire_worktree = projets / slug_projet(cwd) / "memory"

    # Déjà relié : cas courant, dès la deuxième session du worktree. Silencieux.
    if memoire_worktree.is_symlink() or (
        memoire_worktree.is_dir() and memoire_worktree.resolve() == memoire_principale.resolve()
    ):
        return 0

    if memoire_worktree.exists():
        if any(memoire_worktree.iterdir()):
            contexte(
                f"Mémoire de worktree isolée : `{memoire_worktree}` contient déjà des fichiers et "
                f"n'a pas été reliée à celle du dépôt principal (`{memoire_principale}`). "
                "Fusionner à la main, puis supprimer le dossier pour que le lien se fasse."
            )
            return 0
        try:
            memoire_worktree.rmdir()
        except OSError:
            return 0

    try:
        memoire_worktree.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 0

    if creer_lien(memoire_worktree, memoire_principale):
        contexte(
            f"Mémoire du dépôt principal reliée à ce worktree "
            f"(`{memoire_principale}`) : lecture et écriture y tombent."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
