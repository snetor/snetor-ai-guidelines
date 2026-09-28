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
import os
import re
import subprocess
import sys
from pathlib import Path

# --- regles sur les commandes -------------------------------------------------------------

# Un pipe avale le code de sortie de la commande de gauche. Incident : `gh pr checks 94 | tail -4`
# a fait merger #95 sur du rouge, puis `az acr build | tail -20` a masque un token expire, puis la
# meme erreur exactement sur #136. Trois fois en quatre jours.
TRONQUE = r"(tail|head|Select-Object\s+-(First|Last))"

# Une commande COMMENCE une ligne ou suit un separateur — jamais une simple espace.
#
# 🔴 Quatrieme faux positif de ce garde-fou, le 16/09. `\baz\b` matchait « la session az vivante »
# dans le TITRE d'une pull request, et le garde-fou a refuse la creation de la PR qui livrait
# precisement le hook de session Azure. Meme cause que les trois precedents : une regle qui lit ce
# que la commande TRANSPORTE au lieu de ce qu'elle FAIT. `_sans_corps_heredoc` traite le heredoc ;
# ceci traite l'argument cite ordinaire.
#
# ⚠️ Volontairement etroit : `REQUESTS_CA_BUNDLE=... az account show` n'est plus vu, un prefixe de
# variable d'environnement n'etant pas un separateur. C'est le bon sens du compromis — un refus
# manque coute un pipe tronquant de plus, un refus a tort apprend a contourner le garde-fou.
DEBUT_DE_COMMANDE = r"(?:^|[\n;&|(]+\s*)"

# `[^|\n]*` and `QUOTED`: on 2026-09-28 an `az` line inside a multi-line `-m` message made the
# `git push | tail` after it look like an az pipe (alz-security).
QUOTED = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'")
PIPE_QUI_AVALE = [
    (
        re.compile(rf"{DEBUT_DE_COMMANDE}gh\s+pr\s+checks\b[^|\n]*\|\s*{TRONQUE}",
                   re.IGNORECASE | re.MULTILINE),
        "Un pipe avale le code de sortie de `gh pr checks` : la commande rend vert meme quand un "
        "check est rouge. C'est ce qui a fait merger #95 et #136 sur du rouge.\n"
        "Faire : gh pr checks <n> --json name,state  puis LIRE chaque ligne.",
    ),
    (
        re.compile(rf"{DEBUT_DE_COMMANDE}az(?:\.cmd)?\s+[^|\n]*\|\s*{TRONQUE}",
                   re.IGNORECASE | re.MULTILINE),
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
    (
        # Un parametre de serveur pose en CLI vit jusqu'au prochain `terraform apply`, qui
        # retablit la valeur DECLAREE — et personne ne voit passer ce retablissement.
        # `show` et `list` ne sont pas vises : lire n'entre en conflit avec rien.
        re.compile(
            r"\baz\s+(?:postgres|mysql)\s+flexible-server\s+parameter\s+set\b",
            re.IGNORECASE,
        ),
        "Un parametre de serveur declare en Terraform est retabli a sa valeur declaree au "
        "prochain apply, quel qu'en soit le motif. Le 15/09, `citext` posee ainsi dans "
        "`azure.extensions` a ete effacee par un `terraform apply` QUELQUES MINUTES avant que le "
        "job de migration ne tourne : la migration a echoue une seconde fois pour exactement la "
        "meme cause, apres avoir ete « corrigee ».\n"
        "Faire : ajouter le parametre DANS le module Terraform, puis un apply. "
        "Lire reste libre (`parameter show`, `parameter list`).",
    ),
    (
        # `az` ne prend qu'UNE valeur pour `--command` / `--args` : la virgule n'est pas un
        # separateur. Le shape fautif est la virgule ENTRE DEUX VALEURS CITEES — une liste ecrite
        # comme en Python. Une virgule A L'INTERIEUR d'une meme paire de guillemets est legitime.
        re.compile(
            r"\baz\s+containerapp\s+job\s+start\b[^\n]*--(?:command|args)\s+[^\n]*?[\"']\s*,\s*[\"']",
            re.IGNORECASE,
        ),
        "Une virgule entre deux valeurs citees de `--command` / `--args` : `az` n'accepte qu'UNE "
        "valeur, la virgule n'est pas un separateur. Le conteneur demarre sans rien executer et "
        "rend `Failed` SANS UN SEUL LOG — quatre tentatives et 1 h 30 le 15/09, pour un echec qui "
        "ne dit rien.\n"
        "Faire : une seule chaine, le shell a l'interieur — "
        "`--command \"/bin/sh -c 'yarn command:prod upgrade'\"`.",
    ),
]

# Ces trois-la ne sont pas des erreurs : ce sont des gestes difficilement reversibles, ou dont la
# CONCLUSION est fausse. On rend la main a l'humain plutot que de bloquer.
#
# `gh pr merge` est le seul qu'un poste peut lever : variable d'environnement UTILISATEUR Windows
# `SNETOR_GUARD_TRUST_MERGE=1`, posee a la main (`setx`), jamais par `deploy-claude.ps1`. Elle est
# faite pour les postes de l'equipe technique, qui relisent le plan avant de merger. Un power user
# ne la pose pas : chez lui, le merge reste rendu a l'humain. Hors du `settings.json` expres, pour
# qu'un redeploiement ne l'efface pas. Le motif (lire les checks avant) reste la regle.
CONFIANCE_MERGE = "SNETOR_GUARD_TRUST_MERGE"
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
    (
        # Standing rule since 2026-09-28: tf-apply runs only on Clement's explicit go for THAT run.
        # Deliberately not covered by SNETOR_GUARD_TRUST_MERGE: trusting a merge is not trusting
        # an apply. `gh run rerun <id>` is not caught: a run id does not say which workflow it is.
        re.compile(r"\bgh\s+(?:workflow\s+run\b[^\n;&|]*\btf-apply|api\b[^\n;&|]*tf-apply[^\n;&|]*/dispatches)",
                   re.IGNORECASE),
        "Triggering `tf-apply` changes the Azure infrastructure. It needs Clement's explicit go "
        "for this specific run, after he has read the plan.",
    ),
]

# --- az: read freely, change only with a human go -----------------------------------------

# `az` is logged in as an admin account on this workstation: every write goes straight to Azure.
# Standing rule (2026-09-28): read with az; write only for a documented runbook step; any other
# infrastructure change goes through a Terraform PR in azure-landing-zone. A program cannot tell
# a runbook step from an improvised fix (the runbooks use `role assignment create`, `secret set`,
# `job delete`, `restore`...), so a write is handed back to the human, never refused outright.
AZ_INVOCATION = re.compile(rf"{DEBUT_DE_COMMANDE}az(?:\.cmd)?\s+([^\n;&|]*)", re.IGNORECASE | re.MULTILINE)
AZ_WRITE_VERBS = frozenset(
    "create delete update set add remove start stop restart assign import restore register "
    "unregister purge recover deploy up apply reset renew rotate grant revoke attach detach "
    "scale swap invoke upgrade".split()
)
# Local CLI state, not Azure resources: `az account set` picks a subscription, `az config set`
# a default, `az extension add` a plugin.
AZ_LOCAL_GROUPS = frozenset({"login", "logout", "account", "config", "extension", "cloud", "version"})
AZ_REST_WRITE = re.compile(r"(?:--method|-m)\s+[\"']?(?:put|post|patch|delete)\b", re.IGNORECASE)
# POST, but read-only: cost and Resource Graph queries, and the dry run before a resource move.
# Asked by alz-security on 2026-09-28: they run in almost every investigation.
AZ_REST_POST = re.compile(r"(?:--method|-m)\s+[\"']?post\b", re.IGNORECASE)
AZ_REST_READ_POST = re.compile(
    r"(?:Microsoft\.CostManagement/query|Microsoft\.ResourceGraph/resources|/validateMoveResources)\b",
    re.IGNORECASE,
)


def _az_write(commande: str) -> str | None:
    """The first `az` invocation that changes Azure, or None."""
    for m in AZ_INVOCATION.finditer(commande):
        args = m.group(1)
        positional = []
        for token in args.split():
            if token.startswith("-"):
                break
            positional.append(token.lower())
        if not positional or positional[0] in AZ_LOCAL_GROUPS:
            continue
        if positional[0] == "rest":
            if AZ_REST_WRITE.search(args) and not (AZ_REST_POST.search(args) and AZ_REST_READ_POST.search(args)):
                return f"az {args.strip()}"
            continue
        if positional[-1] in AZ_WRITE_VERBS:
            return f"az {' '.join(positional)}"
    return None


# --- gh pr merge: what the merge really does (2026-09-28, alz-security) ------------------------

GH_PR_MERGE = re.compile(r"\bgh\s+pr\s+merge\b([^\n;&|]*)", re.IGNORECASE)
GH_REPO = re.compile(r"(?:^|\s)(?:-R|--repo)(?:\s+|=)(\S+)")
DELETE_BRANCH = re.compile(r"(?:^|\s)(?:--delete-branch|-d)(?:\s|$)")
IMAGE_TAG_FILE = re.compile(r"-image\.auto\.tfvars$")


def _gh(cwd: str, *args: str):
    """`gh ... --json` parsed, or None. Network: only called on a `gh pr merge`."""
    try:
        sortie = subprocess.run(["gh", *args], cwd=cwd, capture_output=True, text=True, timeout=8)
        return json.loads(sortie.stdout) if sortie.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _merge_verdict(commande: str, cwd: str) -> tuple[str, str] | None:
    """Two merges that are not what they look like. Fails open when `gh` does not answer.

    · `--delete-branch` on a PR that another open PR is stacked on closes the stacked PR for
      good. The escalation message warned about it; #504 was still merged that way on
      2026-09-28 and #508 was lost. A warning read and ignored is a recidive: it becomes a deny.
    · A merged `*-image.auto.tfvars` file auto-applies the WHOLE of main in azure-landing-zone,
      not just the tag (#511, 2026-09-28). That merge is an apply: it goes back to the human even
      on a SNETOR_GUARD_TRUST_MERGE workstation.
    """
    m = GH_PR_MERGE.search(commande)
    if not m:
        return None
    args = m.group(1)
    tokens = args.split()
    selector = [tokens[0]] if tokens and not tokens[0].startswith("-") else []
    repo = GH_REPO.search(args)
    repo_args = ["-R", repo.group(1)] if repo else []
    pr = _gh(cwd, "pr", "view", *selector, "--json", "headRefName,files", *repo_args)
    if not isinstance(pr, dict):
        return None
    if DELETE_BRANCH.search(args) and pr.get("headRefName"):
        stacked = _gh(cwd, "pr", "list", "--base", pr["headRefName"], "--state", "open",
                      "--json", "number", *repo_args)
        if stacked:
            numbers = ", ".join(f"#{p['number']}" for p in stacked)
            return "deny", (
                f"{numbers} is stacked on `{pr['headRefName']}`. `--delete-branch` would close it for "
                "good (#508 was lost that way on 2026-09-28).\n"
                f"Do: retarget first (`gh pr edit <n> --base main`), then merge."
            )
    if any(IMAGE_TAG_FILE.search(f.get("path", "")) for f in pr.get("files") or []):
        return "escalate", (
            "This PR changes an `*-image.auto.tfvars` file: merging it auto-applies the whole of main "
            "in azure-landing-zone, not just the tag. Treat the merge as an apply: it needs "
            "Clement's go for this run."
        )
    return None


# --- language: everything written in a repo is in English (2026-09-28) ----------------------

# ponytail: word-count heuristic, not language detection. Two French signals (a function word, an
# elision, one accented letter) are enough; a French quote can be kept inside backticks. Upgrade to
# a real detector only if false positives show up.
FRENCH_WORDS = frozenset(
    "le la les des de une est et pour avec dans sur pas qui que au aux ce cette sans à où".split()
)
FRENCH_ELISION = re.compile(r"^(?:l|d|n|qu|c|s|j)['’]")
FRENCH_ACCENT = re.compile(r"[àâçéèêëîïôùûüœ]", re.IGNORECASE)
WORD = re.compile(r"[a-zà-ÿœ]+(?:['’-][a-zà-ÿœ]+)*")
CODE_SPAN = re.compile(r"`[^`\n]*`")


def _looks_french(text: str) -> bool:
    lines = [l for l in text.splitlines() if not l.strip().lower().startswith("co-authored-by:")]
    text = CODE_SPAN.sub(" ", "\n".join(lines))
    words = WORD.findall(text.lower())
    score = sum(w in FRENCH_WORDS or bool(FRENCH_ELISION.match(w)) for w in words)
    return score + bool(FRENCH_ACCENT.search(text)) >= 2


_QUOTED = r"(?:\s+|=)(?:\"((?:[^\"\\]|\\.)*)\"|'([^']*)'|(\S+))"
COMMIT = re.compile(r"\bgit\s+commit\b", re.IGNORECASE)
COMMIT_MESSAGE = re.compile(rf"(?:^|\s)(?:-m|--message){_QUOTED}")
COMMIT_FILE = re.compile(rf"(?:^|\s)(?:-F|--file){_QUOTED}")
PR_TITLE_CMD = re.compile(r"\bgh\s+pr\s+(?:create|edit|merge)\b", re.IGNORECASE)
PR_TITLE = re.compile(rf"(?:^|\s)(?:-t|--title|--subject){_QUOTED}")


def _heredocs(commande: str) -> list[tuple[str, str]]:
    """`(opening line, body)` of each heredoc — the counterpart of `_sans_corps_heredoc`."""
    found, opening, body, marker = [], "", [], None
    for ligne in commande.split("\n"):
        if marker is not None:
            if ligne.strip() == marker:
                found.append((opening, "\n".join(body)))
                marker = None
            else:
                body.append(ligne)
            continue
        m = _OUVRE_UN_HEREDOC.search(ligne)
        if m:
            opening, body, marker = ligne, [], m.group(1)
    return found


def _values(pattern: re.Pattern, text: str) -> list[str]:
    return [next((g for g in m.groups() if g is not None), "") for m in pattern.finditer(text)]


def _written_texts(commande: str, cwd: str) -> list[str]:
    """Commit messages and PR titles this command is about to write."""
    sans = _sans_corps_heredoc(commande)
    heredocs = _heredocs(commande)
    texts: list[str] = []
    commit = COMMIT.search(sans)
    if commit:
        after = sans[commit.end():]
        texts += _values(COMMIT_MESSAGE, after)
        texts += [body for opening, body in heredocs if COMMIT.search(opening)]
        for path in _values(COMMIT_FILE, after):
            written_here = [body for opening, body in heredocs if path in opening]
            if written_here or path == "-":
                texts += written_here
                continue
            fichier = Path(path) if Path(path).is_absolute() else Path(_cwd_effectif(commande, cwd) or cwd) / path
            try:
                texts.append(fichier.read_text(encoding="utf-8", errors="ignore")[:65536])
            except OSError:
                pass  # missing file: git will say so itself
    pr = PR_TITLE_CMD.search(sans)
    if pr:
        texts += _values(PR_TITLE, sans[pr.end():])
    return texts

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


# Any directory change, wherever it sits: after a separator, or after `do` / `then` in a loop.
_ANY_CD = re.compile(r"(?:^|[;&|(\n]|\bdo\b|\bthen\b)\s*(?:cd|Set-Location|pushd|Push-Location)\s", re.IGNORECASE)


def _cwd_effectif(commande: str, cwd: str) -> str | None:
    """Le repertoire ou la commande s'execute vraiment, `cd` de tete compris.

    None when it cannot be known: a `cd` to a variable, or a `cd` further down the command (inside
    a `for` loop...). Reported by alz-security on 2026-09-28: both fell back to the shared checkout
    on `main` and refused a legitimate worktree commit. An unknown directory skips the branch
    rules — a missed refusal costs less than a wrong one.
    """
    m = _CHANGEMENT_DE_REPERTOIRE.match(commande)
    if len(_ANY_CD.findall(commande)) > (1 if m else 0):
        return None
    if not m:
        return cwd
    cible = next(g for g in m.groups() if g)
    if "$" in cible or "%" in cible:
        return None
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
    # A pipe rule reads the command with quoted text blanked: a commit message line starting with
    # `az` is not an `az` call (2026-09-28). COMMANDES keep the quotes: the comma rule looks inside.
    sans_citations = QUOTED.sub('""', sans_heredoc)
    for motif, message in PIPE_QUI_AVALE:
        if motif.search(sans_citations):
            return "deny", message
    for motif, message in COMMANDES:
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
        git_cwd = _cwd_effectif(commande, cwd)
        branche = _branche(git_cwd) if git_cwd is not None else None
        if branche == "main":
            return "deny", (
                "Commit ou push direct sur `main`. Recidive explicite des 10 et 11/08 — un merge "
                "laisse le checkout sur `main`, et le geste suivant y atterrit.\n"
                "Faire : `git checkout -b <type>/<sujet>` d'abord."
            )
        if re.search(r"\bgit\s+push\b", git_seul) and branche and _branche_deja_mergee(git_cwd, branche):
            return "deny", (
                f"La branche `{branche}` n'apporte plus rien a `origin/main` : sa PR est mergee. "
                "Un commit pousse ici pend hors de `main` — c'est arrive le 06/08.\n"
                "Faire : repartir d'une branche neuve depuis `origin/main`."
            )

    if any(_looks_french(t) for t in _written_texts(commande, cwd)):
        return "deny", (
            "Commit message or PR title in French. Since 2026-09-28 everything written in a repo is "
            "in English (snetor-ai-guidelines: docs/dated/decisions/2026-09-28-english-in-every-repo.md). "
            "Existing French text is not translated.\n"
            "Do: rewrite the message in English. A French quote can stay inside backticks."
        )

    merge = _merge_verdict(sans_heredoc, cwd)
    if merge:
        return merge

    for motif, message in ESCALADE:
        if motif.search(commande):
            if motif is ESCALADE[0][0] and os.environ.get(CONFIANCE_MERGE) == "1":
                continue
            return "escalate", message

    az = _az_write(sans_heredoc)
    if az:
        return "escalate", (
            f"`{az}` changes Azure with an admin account. Allowed only as a step of a documented "
            "runbook; any other infrastructure change goes through a Terraform PR in "
            "azure-landing-zone. Confirm which runbook step this is."
        )
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
