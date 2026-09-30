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


def test_le_controle_de_jeton_azure_est_branche_aux_DEUX_evenements(source):
    """Le branchement `PreToolUse` est celui qui traite l'incident, et il est facile a perdre.

    Le 2026-09-15, la session `az` a expire deux fois EN PLEINE SEQUENCE de montee du fork Twenty
    (`AADSTS70043`, duree de vie 7200 s). Au demarrage de session, le jeton etait vivant les deux
    fois : un controle uniquement en `SessionStart` — ce que faisait l'ancien
    `~/.azure-claude/az-ensure-login.ps1` — ne l'aurait pas vu.

    Ce test echoue donc si quelqu'un retire le second branchement en pensant alleger, ce qui
    ramenerait exactement le defaut d'avant.
    """
    bloc = re.search(
        r"\$jetonDejaBranche\s*=\s*\$false(.*?)Write-Ok\s+\"Contr", source, re.DOTALL
    )
    assert bloc, "bloc de branchement du controle de jeton introuvable dans le deployeur"
    corps = bloc.group(1)
    assert re.search(r"\$cfg\.hooks\.SessionStart\s*=", corps), "branchement SessionStart absent"
    assert re.search(r"\$cfg\.hooks\.PreToolUse\s*=", corps), (
        "branchement PreToolUse absent : une expiration EN COURS de sequence ne serait pas vue, "
        "ce qui est exactement l'incident du 2026-09-15."
    )
    assert "Bash|PowerShell" in corps, "le matcher PreToolUse doit viser les deux outils de shell"


def test_le_controle_de_jeton_azure_est_idempotent(source):
    """Le deployeur tourne plusieurs fois sur un meme poste : il ne doit pas empiler le hook."""
    assert re.search(r"az_ensure_login\\?\.py.*\{\s*\$jetonDejaBranche\s*=\s*\$true", source), (
        "la detection d'un branchement existant ne cherche pas `az_ensure_login.py` : une "
        "deuxieme execution du deployeur ajouterait le hook une seconde fois."
    )


# --- hook startup (2026-09-28) -----------------------------------------------------------------

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"


def test_every_hook_starts_isolated_and_in_utf8(source):
    """Without `-S`, `pip_system_certs.pth` imports pip at each call: 0.9 s idle, over 10 s under
    load, and Claude Code then cancels the guard and runs the command unguarded (CRM run,
    2026-09-24). Without `-X utf8`, French hook messages reach the model as mojibake."""
    commands = re.findall(r"^python .*runpy.*$", source, re.MULTILINE)
    assert len(commands) == 3, commands
    for c in commands:
        assert c.startswith("python -I -S -X utf8 -c "), c


def test_an_existing_hook_entry_is_refreshed_not_just_detected(source):
    for var in ("gardeCommande", "memoireCommande", "jetonCommande"):
        assert re.search(rf"\$h\.command\s*=\s*\${var}\b", source), (
            f"an existing entry keeps its old command: a fix to ${var} never reaches the workstation"
        )


def test_hooks_import_the_stdlib_only():
    """`-S` drops site-packages: a hook that imports a third-party module would crash on start."""
    import ast
    import sys

    for f in HOOKS.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else (
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for n in names:
                top = n.split(".")[0]
                assert top in sys.stdlib_module_names or top == "__future__", f"{f.name}: {n}"


def test_the_guard_runs_with_the_deployed_flags():
    import json
    import subprocess
    import sys

    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "."})
    r = subprocess.run(
        [sys.executable, "-I", "-S", "-X", "utf8", str(HOOKS / "guard.py")],
        input=event, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, r.stderr


def test_the_deployer_refreshes_the_plugin_and_reports_its_version(source):
    """`enabledPlugins` enables a plugin, it never updates one: on 2026-09-28 the author's
    workstation ran 1.11.0 while main shipped 1.13.0, despite `autoUpdate: true`."""
    assert "claude plugin marketplace update snetor-ai-guidelines" in source
    assert "$refreshed = @('snetor-skills')" in source
    assert 'claude plugin update "$p@snetor-ai-guidelines"' in source
    assert "installed_plugins.json" in source, "the installed version is never compared to the repo"


def test_the_deployer_never_enables_the_tech_team_plugin(source):
    """`snetor-dev` is for developer workstations only: the deployer refreshes it where a
    developer installed it, and must never put it in the list it enables for everyone."""
    enabled = re.search(r"\$snetorPlugins\s*=\s*\[ordered\]@\{(.*?)\}", source, re.S).group(1)
    assert "snetor-skills@snetor-ai-guidelines" in enabled
    assert "snetor-dev" not in enabled
    assert "-contains 'snetor-dev@snetor-ai-guidelines'" in source
