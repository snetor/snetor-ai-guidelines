"""Garde-fou `PreToolUse` Snetor : refuse les gestes qui ont deja coute quelque chose.

Chaque regle ci-dessous correspond a un incident REEL, la plupart annotes « recidive » ou
« troisieme variante » — c'est-a-dire des lecons ecrites, relues, et refaites quand meme. Une
lecon qu'on repete est une lecon qui demande un mecanisme, pas une phrase de plus.

Ne pas confondre les deux moities du systeme : `tasks/lessons.md` porte les regles de JUGEMENT,
qu'aucun programme ne saura verifier ; ce fichier porte celles qu'une machine peut refuser. Toute
regle qui migre de l'un vers l'autre est une regle qu'on retire du texte ET qui devient vraiment
respectee. C'est le seul mouvement qui allege la doctrine et durcit la pratique en meme temps.

## Portee

Ce garde-fou etait local a `snetor-pim` jusqu'au 10/09/2026 : ses neuf regles protegeaient un
depot sur quatorze, pendant que les treize autres n'avaient contre les memes erreurs que de la
prose. Il est desormais deploye sur le poste par `scripts/deploy-claude.ps1`, donc actif sur TOUS
les depots ouverts avec Claude Code.

Les regles sont volontairement ETROITES : celles qui ne concernent pas un depot ne s'y declenchent
tout simplement jamais. Un depot qui a besoin d'une regle en propre pose son propre hook dans son
`.claude/settings.json` — il s'ajoute a celui-ci, il ne le remplace pas.

Contrat du hook (documentation Claude Code) :
  · l'evenement arrive en JSON sur stdin : `tool_name`, `tool_input`, `cwd`, ...
  · sortie 2  -> l'appel est bloque, stderr est rendu au modele comme motif ;
  · sortie 0  -> l'appel passe, sauf JSON `permissionDecision` sur stdout ;
  · `escalate` -> la main est rendue a l'humain. Reserve a ce qui est difficilement reversible.

Regle de conception : une regle qui se declenche a tort est une regle desactivee dans la semaine.
Les motifs sont donc etroits, et chacun cite l'incident qui le justifie.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# --- regles sur les commandes -------------------------------------------------------------

# Un pipe avale le code de sortie de la commande de gauche. Incident : `gh pr checks 94 | tail -4`
# a fait merger #95 sur du rouge, puis `az acr build | tail -20` a masque un token expire, puis la
# meme erreur exactement sur #136. Trois fois en quatre jours.
TRONQUE = r"(tail|head|Select-Object\s+-(First|Last))"
PIPE_QUI_AVALE = [
    (
        re.compile(rf"\bgh\s+pr\s+checks\b[^|]*\|\s*{TRONQUE}", re.IGNORECASE),
        "Un pipe avale le code de sortie de `gh pr checks` : la commande rend vert meme quand un "
        "check est rouge. C'est ce qui a fait merger #95 et #136 sur du rouge.\n"
        "Faire : gh pr checks <n> --json name,state  puis LIRE chaque ligne.",
    ),
    (
        re.compile(rf"\baz\s+[^|]*\|\s*{TRONQUE}", re.IGNORECASE),
        "Un pipe tronquant derriere `az` masque a la fois la fin de la sortie et le code de "
        "sortie. Incident : 20 minutes perdues sur un token expire invisible.\n"
        "Faire : rediriger vers un fichier, ou lire la sortie JSON en entier.",
    ),
]

COMMANDES = [
    (
        # `az acr build` ecrit ses journaux avec la page de codes du poste (cp1252) et plante
        # dessus. `PYTHONIOENCODING` ne traverse pas `az.cmd`.
        re.compile(r"\baz\s+acr\s+build\b(?!.*--no-logs)", re.IGNORECASE | re.DOTALL),
        "`az acr build` plante en ecrivant ses journaux (cp1252 sur ce poste). Ajouter "
        "`--no-logs` et lire le JSON rendu.",
    ),
    (
        # Un `;` n'est pas un `&&` : le `start` part meme si l'`update` a echoue. Deux executions
        # sont parties en mauvaise configuration comme ca.
        re.compile(r"\baz\b[^;]*\bupdate\b[^;]*;\s*az\b[^;]*\bstart\b", re.IGNORECASE),
        "Un `;` entre `az ... update` et `az ... start` lance le job meme si la mise a jour a "
        "echoue — deux executions sont parties en mauvaise configuration.\n"
        "Faire : verifier le retour de l'update avant de demarrer.",
    ),
]

# Ces trois-la ne sont pas des erreurs : ce sont des gestes difficilement reversibles, ou dont la
# CONCLUSION est fausse. On rend la main a l'humain plutot que de bloquer.
ESCALADE = [
    (
        re.compile(r"\bgh\s+pr\s+merge\b", re.IGNORECASE),
        "`gh pr merge` ne regarde pas les checks. Confirmer que `gh pr checks <n> --json "
        "name,state` a ete lu ligne par ligne avant de merger.\n"
        "⚠️ Dans une PILE de PR : recibler d'abord (`gh pr edit <n> --base main`), merger ensuite. "
        "`--delete-branch` sur une PR de base ferme la PR empilee, et elle ne se rouvre pas.",
    ),
    (
        # Quatrieme habillage de la famille « code de sortie qui ment » : `--watch` est sorti en 0
        # alors qu'un check etait rouge. Attendre est legitime — conclure ne l'est pas.
        re.compile(r"\bgh\s+pr\s+checks\b[^\n]*--watch\b", re.IGNORECASE),
        "`gh pr checks --watch` est deja sorti en 0 avec un check ROUGE. Le code de sortie d'un "
        "outil de surveillance n'est pas un verdict de CI.\n"
        "Faire : apres le `--watch`, relancer `gh pr checks <n> --json name,state` et lire chaque "
        "ligne.",
    ),
    (
        re.compile(r"\bgit\s+push\b.*(--force(?!-with-lease)|(^|\s)-f(\s|$))"),
        "`git push --force` reecrit l'historique distant.",
    ),
]

# --- regles specifiques a PowerShell ------------------------------------------------------

NON_ASCII = re.compile(r"[^\x00-\x7F]")
ECRITURE_PS = re.compile(r"\b(Set-Content|Out-File|Add-Content)\b", re.IGNORECASE)
COMMIT_INLINE = re.compile(r"\bgit\s+commit\b[^\n]*\s-m\s+[\"']", re.IGNORECASE)
# PowerShell ne connait pas les heredocs — recidive, c'est deja dans CLAUDE.md. L'ancre de fin de
# ligne est ce qui epargne `Select-String "<<<<<<<"`, ou les chevrons ne terminent pas la ligne.
HEREDOC = re.compile(r"(^|\s)<<[-~]?\s*(['\"]?)[A-Za-z_]\w*\2\s*$", re.MULTILINE)


def _branche(cwd: str) -> str | None:
    try:
        sortie = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return sortie.stdout.strip() if sortie.returncode == 0 else None


# Un `cd` ou un `Set-Location` en tete de commande change l'arbre sur lequel `git` s'execute.
# ⚠️ Sans ca, le garde-fou lisait la branche du checkout PARTAGE (souvent `main`) et refusait tout
# travail en WORKTREE — c'est-a-dire exactement le mode de travail que `CLAUDE.md` impose quand
# plusieurs sessions partagent le depot. Signale par une session parallele le 14/08, apres qu'elle
# se soit fait ecraser deux fois dans le checkout partage.
_CHANGEMENT_DE_REPERTOIRE = re.compile(
    r"^\s*(?:cd|Set-Location(?:\s+-Path)?)\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s;&|]+))",
    re.IGNORECASE,
)


def _cwd_effectif(commande: str, cwd: str) -> str:
    """Le repertoire ou la commande s'execute vraiment, `cd` de tete compris."""
    m = _CHANGEMENT_DE_REPERTOIRE.match(commande)
    if not m:
        return cwd
    cible = next(g for g in m.groups() if g)
    chemin = Path(cible)
    if not chemin.is_absolute():
        chemin = Path(cwd) / chemin
    try:
        return str(chemin) if chemin.is_dir() else cwd
    except OSError:
        return cwd


def _git(cwd: str, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _branche_deja_mergee(cwd: str, branche: str | None = None) -> bool:
    """Vrai si la branche courante n'apporte plus rien a `origin/main` — donc deja mergee.

    Apres un squash merge, la branche locale survit et un commit pousse dessus pend hors de
    `main`. C'est arrive le 06/08.

    ⚠️ Une branche NEUVE n'apporte rien non plus a `origin/main` : sans le test ci-dessous, le
    garde-fou refusait le tout premier `git push -u` d'une branche fraiche (rencontre le 14/08).
    Une branche qui n'a jamais ete poussee n'a par definition pas de PR mergee.

    🔴 Le discriminant est la REFERENCE DISTANTE, plus l'amont configure (30/08). `git worktree
    add -b <nom> <chemin> origin/main` pose le suivi tout seul : la branche a donc un amont a la
    seconde ou elle nait, et l'ancien test la prenait pour une branche mergee. La reference
    `refs/remotes/origin/<branche>`, elle, n'apparait qu'apres un push ou un fetch — c'est
    exactement « a deja ete poussee ».
    """
    branche = branche or _branche(cwd)
    if not branche:
        return False
    ref = _git(cwd, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branche}")
    if ref is None or ref.returncode != 0:
        return False  # jamais poussee : rien a merger, donc rien a refuser
    sortie = _git(cwd, "log", "origin/main..HEAD", "--oneline")
    return sortie is not None and sortie.returncode == 0 and not sortie.stdout.strip()


# Un heredoc ouvre un CONTENU, pas une commande. Ce qu'il porte — un message de commit, un corps de
# PR, une lecon — n'est pas ce que le shell va executer.
_OUVRE_UN_HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")


def _sans_corps_heredoc(commande: str) -> str:
    """Retire le CONTENU des heredocs, en gardant les lignes de commande.

    🔴 Incident du 30/08, deux fois dans la meme heure. `git commit -F <fichier>` a ete refuse au
    motif « la branche a deja ete mergee », sur une branche creee deux minutes plus tot. La regle
    `git push` s'etait declenchee parce que la chaine `push` figurait dans le MESSAGE DE COMMIT
    (`pim_acr_push`), ecrit juste avant dans un heredoc de la meme ligne de commande. Puis la meme
    chose sur un texte de lecons qui citait `git commit -m`.

    Un garde-fou doit se declencher sur ce que la commande FAIT. Le contenu qu'elle transporte est
    de la donnee : le lire comme du code produit des refus incomprehensibles, et un refus
    incomprehensible apprend a contourner le garde-fou.
    """
    lignes = commande.split("\n")
    gardees: list[str] = []
    marqueur: str | None = None
    for ligne in lignes:
        if marqueur is not None:
            if ligne.strip() == marqueur:
                marqueur = None
            continue
        gardees.append(ligne)
        m = _OUVRE_UN_HEREDOC.search(ligne)
        if m:
            marqueur = m.group(1)
    return "\n".join(gardees)


# Une invocation `git push` s'arrete au premier separateur : le reste de la ligne appartient a une
# autre commande ou a un commentaire.
_INVOCATION_PUSH = re.compile(r"\bgit\s+push\b([^\n;&|#]*)")
_SUPPRIME_UNE_REFERENCE = re.compile(r"(^|\s)(--delete|-d|--prune)(\s|$)")


def _que_des_suppressions(commande: str) -> bool:
    """Vrai si la commande ne contient QUE des `git push` qui suppriment une reference distante.

    ⚠️ `git push origin --delete <branche>` n'ecrit rien sur la branche courante : il supprime une
    reference. Le compter comme « push sur `main` » a bloque le nettoyage des branches mergees le
    17/08 — troisieme faux positif de ce garde-fou, et ce nettoyage est precisement ce que
    `CLAUDE.md` prescrit.

    `all()` et non `any()` : si une seule des invocations pousse vraiment, l'exemption tombe. Sans
    ca, `git push origin main` suivi d'un `--delete` plus loin dans la ligne passerait — teste.
    """
    invocations = _INVOCATION_PUSH.findall(commande)
    return bool(invocations) and all(_SUPPRIME_UNE_REFERENCE.search(a) for a in invocations)


def verifier_commande(commande: str, powershell: bool, cwd: str) -> tuple[str, str] | None:
    """Rend `(decision, motif)` ou `None`. `decision` vaut `deny` ou `escalate`."""
    # ⚠️ Ces regles lisent la commande PRIVEE du corps de ses heredocs, pour la meme raison que les
    # regles git plus bas : un texte qui CITE `az … | tail` n'execute pas `az`. Rencontre le 30/08
    # en documentant `az login --claims-challenge` dans le HANDOFF — le contournement etait alors
    # d'ecrire la commande autrement, c'est-a-dire d'obeir a un garde-fou qui se trompait.
    sans_heredoc = _sans_corps_heredoc(commande)
    for motif, message in PIPE_QUI_AVALE + COMMANDES:
        if motif.search(sans_heredoc):
            return "deny", message

    if powershell and ECRITURE_PS.search(commande) and NON_ASCII.search(commande):
        return "deny", (
            "`Set-Content` / `Out-File` corrompt un fichier accentue sur ce poste — 135 marqueurs "
            "mojibake ont ete commites le 07/08, apres que la lecon eut deja ete ecrite le 03/08.\n"
            "Faire : l'outil d'edition, ou Python avec `encoding=\"utf-8\"`."
        )

    if powershell and HEREDOC.search(commande):
        return "deny", (
            "PowerShell ne connait pas les heredocs `<<'EOF'` : le contenu part en arguments et la "
            "commande casse en silence. C'est deja ecrit dans `CLAUDE.md`.\n"
            "Faire : ecrire le contenu dans un fichier (outil d'edition), puis le passer par "
            "`-F` / `--body-file`. Ou utiliser l'outil Bash, ou les heredocs fonctionnent."
        )

    if powershell and COMMIT_INLINE.search(commande):
        return "deny", (
            "PowerShell 5.1 re-tokenise les arguments d'un executable natif : `git commit -m \"...\"` "
            "casse des que le message contient un guillemet.\n"
            "Faire : `git commit -F <fichier>`, et `gh pr create --body-file`."
        )

    # ⚠️ Les regles git se lisent sur la commande PRIVEE du corps de ses heredocs : un message de
    # commit qui cite `git push` n'est pas un `git push`. Cf. `_sans_corps_heredoc`.
    git_seul = _sans_corps_heredoc(commande)
    if re.search(r"\bgit\s+(push|commit)\b", git_seul) and not _que_des_suppressions(git_seul):
        cwd = _cwd_effectif(commande, cwd)
        branche = _branche(cwd)
        if branche == "main":
            return "deny", (
                "Commit ou push direct sur `main`. Recidive explicite des 10 et 11/08 — un merge "
                "laisse le checkout sur `main`, et le geste suivant y atterrit.\n"
                "Faire : `git checkout -b <type>/<sujet>` d'abord."
            )
        if re.search(r"\bgit\s+push\b", git_seul) and branche and _branche_deja_mergee(cwd, branche):
            return "deny", (
                f"La branche `{branche}` n'apporte plus rien a `origin/main` : sa PR est mergee. "
                "Un commit pousse ici pend hors de `main` — c'est arrive le 06/08.\n"
                "Faire : repartir d'une branche neuve depuis `origin/main`."
            )

    for motif, message in ESCALADE:
        if motif.search(commande):
            return "escalate", message
    return None


INIT_SOUS_TESTS = re.compile(r"[\\/]tests?[\\/].*__init__\.py$")


def verifier_ecriture(chemin: str, cwd: str) -> tuple[str, str] | None:
    """Bloque une ecriture dans le depot quand le checkout est sur `main`."""
    if not chemin:
        return None
    try:
        Path(chemin).resolve().relative_to(Path(cwd).resolve())
    except (ValueError, OSError):
        return None  # hors du depot : bloc-notes, fichier temporaire, autre projet

    if INIT_SOUS_TESTS.search(chemin):
        return "deny", (
            "Un `__init__.py` sous un repertoire de tests casse la collecte pytest "
            "(`--import-mode=importlib` et `rootdir` s'y perdent). Le piege se paie une fois par "
            "nouveau module de tests.\nFaire : ne pas creer ce fichier — les tests n'ont pas "
            "besoin d'etre un paquet."
        )

    # La branche se lit dans l'arbre du FICHIER, pas dans celui de la session : un worktree vit
    # sous `.claude/worktrees/<nom>/` et porte sa propre branche. Lire `cwd` refuserait toute
    # ecriture en worktree sous pretexte que le checkout partage est sur `main`.
    if _branche(str(Path(chemin).parent)) != "main":
        return None
    return "deny", (
        f"Ecriture dans `{Path(chemin).name}` alors que le checkout est sur `main`. Une branche = "
        "une PR = un sujet.\nFaire : `git checkout -b <type>/<sujet>` d'abord, ou travailler dans "
        "un worktree."
    )


def main() -> int:
    try:
        evenement = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # un garde-fou qui casse la session est pire que le defaut qu'il previent

    outil = evenement.get("tool_name", "")
    entree = evenement.get("tool_input") or {}
    cwd = evenement.get("cwd") or "."

    if outil in ("Bash", "PowerShell"):
        verdict = verifier_commande(entree.get("command", ""), outil == "PowerShell", cwd)
    elif outil in ("Write", "Edit", "NotebookEdit"):
        verdict = verifier_ecriture(entree.get("file_path", ""), cwd)
    else:
        verdict = None

    if verdict is None:
        return 0

    decision, motif = verdict
    if decision == "escalate":
        json.dump(
            {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "escalate",
                "permissionDecisionReason": motif,
            }},
            sys.stdout,
        )
        return 0

    print(motif, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
