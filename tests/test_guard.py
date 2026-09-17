"""Le garde-fou attrape ce qu'il doit, et laisse passer ce qui est legitime.

La deuxieme moitie compte autant que la premiere : une regle qui se declenche a tort est une regle
desactivee dans la semaine. Chaque faux positif de l'historique a ici son test, avec l'incident qui
l'a revele — 14/08, 17/08, 30/08 — parce qu'une regression sur ces cas-la ne se voit pas : elle se
manifeste par un refus incomprehensible, et un refus incomprehensible apprend a contourner le
garde-fou plutot qu'a le corriger.

Suite ecrite dans `snetor-pim`, rapatriee ici le 2026-09-10 avec le garde-fou lui-meme.
"""

from __future__ import annotations

import pytest

import guard  # `tests/conftest.py` met `hooks/` sur le chemin


@pytest.fixture
def hors_main(monkeypatch):
    """Neutralise les regles de branche pour tester les autres isolement."""
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "feat/quelque-chose")
    monkeypatch.setattr(guard, "_branche_deja_mergee", lambda _cwd, _b=None: False)


def verdict(commande, powershell=False, cwd="."):
    return guard.verifier_commande(commande, powershell, cwd)


# --- ce qui doit etre bloque ---------------------------------------------------------------

@pytest.mark.parametrize(
    "commande",
    [
        "gh pr checks 94 | tail -4",
        "gh pr checks 136 --watch | head -20",
        "az containerapp job execution list -n caj-pim-migrate-dev | tail -5",
        "az acr build --registry acrpimdeva6cc --image pim-worker:v3 ingestion/",
        "az containerapp job update -n caj --image x ; az containerapp job start -n caj",
    ],
)
def test_les_gestes_qui_ont_deja_coute_sont_refuses(commande, hors_main):
    assert verdict(commande) is not None, f"non attrape : {commande}"
    assert verdict(commande)[0] == "deny"


def test_set_content_sur_contenu_accentue_est_refuse(hors_main):
    v = verdict('Set-Content -Path runbook.md -Value "peuplement terminé"', powershell=True)
    assert v is not None and v[0] == "deny"
    assert "mojibake" in v[1]


def test_commit_inline_en_powershell_est_refuse(hors_main):
    v = verdict('git commit -m "fix: le libelle "brut" cassait"', powershell=True)
    assert v is not None and v[0] == "deny"
    assert "-F" in v[1]


@pytest.mark.parametrize(
    "commande",
    [
        "git push origin --delete docs/arbitrages-metier-14-08",
        "git push origin -d feat/vieille-branche",
        "git push --prune origin",
    ],
)
def test_supprimer_une_branche_distante_depuis_main_est_autorise(commande, monkeypatch):
    """Faux positif rencontre le 17/08 : le nettoyage des branches mergees etait refuse.

    `git push --delete` supprime une reference distante, il n'ecrit rien sur la branche courante.
    Le confondre avec un push sur `main` bloquait exactement ce que `CLAUDE.md` prescrit — ne pas
    laisser trainer de branches mergees.
    """
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "main")
    assert verdict(commande) is None, f"faux positif : {commande}"


def test_un_vrai_push_sur_main_reste_refuse_meme_avec_delete_ailleurs(monkeypatch):
    """Le mot `delete` ailleurs dans la commande ne doit pas servir de passe-droit."""
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "main")
    monkeypatch.setattr(guard, "_branche_deja_mergee", lambda _cwd, _b=None: False)
    v = verdict("git push origin main  # apres avoir fait git branch --delete vieille")
    assert v is not None and v[0] == "deny"


def test_commit_sur_main_est_refuse(monkeypatch):
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "main")
    v = verdict("git commit -F message.txt")
    assert v is not None and v[0] == "deny"
    assert "checkout -b" in v[1]


def test_push_sur_branche_deja_mergee_est_refuse(monkeypatch):
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "feat/deja-mergee")
    monkeypatch.setattr(guard, "_branche_deja_mergee", lambda _cwd, _b=None: True)
    v = verdict("git push")
    assert v is not None and v[0] == "deny"
    assert "pend hors de `main`" in v[1]


def test_un_message_de_commit_qui_cite_push_n_est_pas_un_push(monkeypatch, hors_main):
    """Faux positif rencontre le 30/08 : DEUXIEME fois que ce garde-fou refuse un geste correct.

    Le message de commit d'une PR d'infrastructure citait `pim_acr_push` -- le nom d'une ressource
    Terraform. Le test `"push" in commande` l'a trouve, et le commit a ete refuse au motif que la
    PR de la branche etait mergee. La branche avait deux minutes.

    Un garde-fou doit lire ce que la commande FAIT, jamais ce qu'elle transporte.
    """
    monkeypatch.setattr(guard, "_branche_deja_mergee", lambda _cwd, _b=None: True)
    commande = (
        "cat > /tmp/msg.txt <<'EOF'\n"
        "feat(pim): declarer le role\n"
        "\n"
        "Meme motif que `pim_acr_push` : le SP de CI ne peut pas ecrire de role assignment.\n"
        "EOF\n"
        "git commit -F /tmp/msg.txt"
    )
    assert verdict(commande) is None


def test_un_heredoc_qui_cite_git_commit_m_ne_declenche_pas_la_regle_powershell(hors_main):
    """Meme incident, autre regle : un texte de lecons citait `git commit -m \"...\"`.

    Le contenu d'un heredoc n'est pas execute par PowerShell -- il est ecrit dans un fichier.
    """
    commande = (
        "python - <<'PY'\n"
        "texte = 'PowerShell 5.1 re-tokenise : git commit -m \"...\" casse'\n"
        "PY"
    )
    assert verdict(commande) is None


def test_un_heredoc_qui_cite_une_commande_az_ne_declenche_pas_la_regle_du_pipe(hors_main):
    """Troisieme incident du meme genre, 30/08 : documenter une commande `az` dans le HANDOFF.

    Le correctif du matin n'avait ete applique qu'aux regles git ; la regle du pipe tronquant, elle,
    lisait toujours la commande entiere. Ecrire `az login --claims-challenge` dans un heredoc, avec
    un `| tail` sur la VRAIE commande, etait refuse -- et le contournement consistait a mal
    documenter la commande, c'est-a-dire a obeir a un garde-fou qui se trompait.
    """
    commande = (
        "python - <<'PY'\n"
        "texte = 'Une suppression exige `az login --claims-challenge <b64>`.'\n"
        "PY\n"
        "check_docs.py --fix | tail -3"
    )
    assert verdict(commande) is None


def test_un_vrai_pipe_tronquant_derriere_az_reste_refuse(hors_main):
    """La regle mord toujours quand `az` est REELLEMENT invoque."""
    v = verdict("az containerapp job show -n j -g rg | head -5")
    assert v is not None and v[0] == "deny"


def test_une_branche_avec_un_amont_mais_jamais_poussee_n_est_pas_mergee(monkeypatch):
    """`git worktree add -b <nom> <chemin> origin/main` pose le SUIVI a la creation.

    L'ancien discriminant (« a un amont configure ») etait donc vrai des la naissance de la
    branche. Le bon discriminant est la reference distante, qui n'existe qu'apres un push.
    """
    def sans_reference_distante(_cwd, *args):
        if args[:2] == ("rev-parse", "--verify"):
            return _Sortie(code=1)            # refs/remotes/origin/<branche> absente
        return _Sortie(out="")                # rien devant origin/main
    monkeypatch.setattr(guard, "_git", sans_reference_distante)
    assert guard._branche_deja_mergee(".", "feat/toute-neuve") is False


class _Sortie:
    def __init__(self, code=0, out=""):
        self.returncode, self.stdout = code, out


def test_une_branche_neuve_jamais_poussee_n_est_pas_prise_pour_une_branche_mergee(monkeypatch):
    """Faux positif rencontre le 14/08 : le tout premier `git push -u` etait refuse.

    Une branche fraiche n'apporte rien a `origin/main`, exactement comme une branche mergee.
    Ce qui les separe : la neuve n'a pas de reference distante.
    """
    def sans_reference_distante(_cwd, *args):
        if args[:2] == ("rev-parse", "--verify"):
            return _Sortie(code=1)            # refs/remotes/origin/<branche> n'existe pas
        return _Sortie(out="")                # rien devant origin/main
    monkeypatch.setattr(guard, "_git", sans_reference_distante)
    assert guard._branche_deja_mergee(".", "feat/neuve") is False


def test_une_branche_poussee_et_videe_par_le_squash_merge_est_bien_detectee(monkeypatch):
    def avec_reference_distante(_cwd, *args):
        if args[:2] == ("rev-parse", "--verify"):
            return _Sortie(out="abc1234")     # refs/remotes/origin/<branche> existe
        return _Sortie(out="")                # plus rien devant origin/main
    monkeypatch.setattr(guard, "_git", avec_reference_distante)
    assert guard._branche_deja_mergee(".", "feat/x") is True


def test_ecriture_sur_main_est_refusee(monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "main")
    fichier = tmp_path / "sql" / "119_x.sql"
    fichier.parent.mkdir()
    fichier.write_text("-- x", encoding="utf-8")
    v = guard.verifier_ecriture(str(fichier), str(tmp_path))
    assert v is not None and v[0] == "deny"


# --- ce qui doit etre rendu a l'humain -----------------------------------------------------

@pytest.mark.parametrize(
    "commande",
    [
        "gh pr merge 161 --squash",
        "git push --force origin main",
        "gh pr checks 166 --watch",      # sorti en 0 avec un check rouge, le 14/08
    ],
)
def test_les_gestes_difficilement_reversibles_remontent_a_l_humain(commande, hors_main):
    v = verdict(commande)
    assert v is not None and v[0] == "escalate", f"attendu escalate pour : {commande}"


def test_un_heredoc_en_powershell_est_refuse(hors_main):
    v = verdict("git commit -F - <<'EOF'\nun message\nEOF", powershell=True)
    assert v is not None and v[0] == "deny"
    assert "heredoc" in v[1]


def test_un_init_sous_un_repertoire_de_tests_est_refuse(tmp_path):
    cible = tmp_path / "ingestion" / "tests" / "nouveau" / "__init__.py"
    cible.parent.mkdir(parents=True)
    v = guard.verifier_ecriture(str(cible), str(tmp_path))
    assert v is not None and v[0] == "deny"
    assert "collecte pytest" in v[1]


# --- ce qui doit passer --------------------------------------------------------------------

@pytest.mark.parametrize(
    "commande",
    [
        "gh pr checks 161 --json name,state",
        "az acr build --no-logs --registry acrpimdeva6cc --image pim-worker:v3 ingestion/",
        "az containerapp job execution list -n caj-pim-migrate-dev -o json",
        "az account show | ConvertFrom-Json",           # pipe non tronquant
        "git push -u origin feat/alignement-metier",
        "git commit -F message.txt",
        "pytest -q",
        "ls | head -20",                                 # ni gh ni az : pas notre affaire
        "git push --force-with-lease",                   # explicitement plus sur que --force
        "gh run watch 4821",                             # ce n'est pas `gh pr checks`
    ],
)
def test_les_commandes_legitimes_passent(commande, hors_main):
    assert verdict(commande) is None, f"faux positif : {commande}"


@pytest.mark.parametrize(
    "commande",
    [
        'git diff | Select-String "<<<<<<<"',   # les chevrons ne terminent pas la ligne
        "git commit -F message.txt",
        "$texte = @'\nun here-string PowerShell\n'@",   # syntaxe PS legitime, pas un heredoc
    ],
)
def test_le_motif_heredoc_epargne_ce_qui_est_legitime(commande, hors_main):
    assert verdict(commande, powershell=True) is None, f"faux positif : {commande}"


@pytest.mark.parametrize(
    "chemin",
    [
        "ingestion/src/consolidation/__init__.py",   # un vrai paquet, pas des tests
        "ingestion/tests/claude/test_guard.py",      # un test, pas un __init__
        "app/src/latest/__init__.py",                # `latest` n'est pas `tests`
    ],
)
def test_les_ecritures_legitimes_passent(chemin, tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "feat/x")
    cible = tmp_path / chemin
    cible.parent.mkdir(parents=True, exist_ok=True)
    assert guard.verifier_ecriture(str(cible), str(tmp_path)) is None, f"faux positif : {chemin}"


def test_une_ecriture_hors_du_depot_passe_meme_sur_main(monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "_branche", lambda _cwd: "main")
    ailleurs = tmp_path / "ailleurs" / "note.md"
    ailleurs.parent.mkdir()
    ailleurs.write_text("x", encoding="utf-8")
    depot = tmp_path / "depot"
    depot.mkdir()
    assert guard.verifier_ecriture(str(ailleurs), str(depot)) is None


# --- le worktree, que le garde-fou refusait --------------------------------------------------

def test_un_set_location_en_tete_deplace_l_arbre_lu(tmp_path):
    """Signale par une session parallele le 14/08 : tout travail en worktree etait refuse.

    `cwd` est le repertoire de la SESSION — le checkout partage, souvent sur `main`. La commande,
    elle, s'execute apres un `cd` ou un `Set-Location` vers le worktree, qui porte sa propre
    branche. Lire `cwd` refusait donc le mode de travail que `CLAUDE.md` impose.
    """
    partage = tmp_path / "snetor-pim"
    worktree = partage / ".claude" / "worktrees" / "essai"
    worktree.mkdir(parents=True)

    assert guard._cwd_effectif(f'Set-Location "{worktree}"\ngit commit -F m.txt', str(partage)) == str(worktree)
    assert guard._cwd_effectif(f"cd {worktree} && git push", str(partage)) == str(worktree)
    # Chemin relatif : resolu depuis le cwd de la session.
    assert guard._cwd_effectif("cd .claude/worktrees/essai && git push", str(partage)) == str(worktree)
    # Pas de changement de repertoire, ou cible inexistante : on garde le cwd de la session.
    assert guard._cwd_effectif("git push", str(partage)) == str(partage)
    assert guard._cwd_effectif("cd /nexiste/pas && git push", str(partage)) == str(partage)


def test_un_commit_dans_un_worktree_passe_meme_si_la_session_est_sur_main(tmp_path, monkeypatch):
    partage = tmp_path / "snetor-pim"
    worktree = partage / ".claude" / "worktrees" / "essai"
    worktree.mkdir(parents=True)
    # Le checkout partage est sur `main`, le worktree sur une branche de travail.
    monkeypatch.setattr(guard, "_branche", lambda cwd: "main" if cwd == str(partage) else "chore/x")
    monkeypatch.setattr(guard, "_branche_deja_mergee", lambda _cwd, _b=None: False)

    assert verdict(f'Set-Location "{worktree}"\ngit commit -F m.txt', cwd=str(partage)) is None
    # Et sans le deplacement, le refus reste : c'est bien la session qui est sur `main`.
    v = verdict("git commit -F m.txt", cwd=str(partage))
    assert v is not None and v[0] == "deny"


def test_une_ecriture_lit_la_branche_de_l_arbre_du_fichier(tmp_path, monkeypatch):
    partage = tmp_path / "snetor-pim"
    worktree = partage / ".claude" / "worktrees" / "essai" / "sql"
    worktree.mkdir(parents=True)
    fichier = worktree / "119_x.sql"
    fichier.write_text("-- x", encoding="utf-8")
    monkeypatch.setattr(guard, "_branche", lambda cwd: "main" if cwd == str(partage) else "chore/x")

    assert guard.verifier_ecriture(str(fichier), str(partage)) is None


def test_un_evenement_illisible_ne_casse_pas_la_session(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("pas du json"))
    assert guard.main() == 0


# --- cas ajoutes au rapatriement (2026-09-10) -------------------------------------------------

def test_powershell_select_object_compte_comme_une_troncature(hors_main):
    """`TRONQUE` connait `Select-Object -First`, mais rien ne le verifiait.

    C'est la forme PowerShell du meme piege, et c'est elle qui a masque un build non parti le
    2026-08-19 : trois lignes coupees pour la lisibilite, et une revision Container Apps a pris
    100 % du trafic sur une image inexistante.
    """
    v = verdict("az acr repository show-tags --name acr | Select-Object -First 3", powershell=True)
    assert v is not None and v[0] == "deny"


def test_set_content_accentue_en_bash_passe(hors_main):
    """La regle vise la re-tokenisation de PowerShell, pas l'ecriture en general."""
    assert verdict('Set-Content -Path a.md -Value "clé"', powershell=False) is None


def test_heredoc_en_bash_passe(hors_main):
    """Les heredocs fonctionnent sous bash : la regle ne doit mordre qu'en PowerShell."""
    assert verdict("python - <<'PY'\nprint(1)\nPY", powershell=False) is None


def test_un_chemin_d_ecriture_vide_passe():
    assert guard.verifier_ecriture("", ".") is None


def test_le_corps_d_un_heredoc_est_bien_retire_de_la_commande():
    """Test direct de l'aide, la ou les autres l'eprouvent a travers un verdict."""
    commande = "git commit -F - <<'EOF'\nparle de git push --force\nEOF\necho fini"
    nettoye = guard._sans_corps_heredoc(commande)
    assert "--force" not in nettoye
    assert "echo fini" in nettoye


# --- cas ajoutes apres la montee du fork Twenty (2026-09-14 au 2026-09-16) --------------------

@pytest.mark.parametrize(
    "commande",
    [
        'az postgres flexible-server parameter set -g rg-twenty-dev -s psql-twenty-dev '
        '-n azure.extensions -v "uuid-ossp,unaccent,citext"',
        "az mysql flexible-server parameter set -n sql_mode -v ANSI --resource-group rg-x "
        "--server-name srv-x",
    ],
)
def test_un_parametre_de_serveur_pose_en_cli_est_refuse(commande, hors_main):
    """Terraform retablit la valeur declaree au prochain apply, et personne ne le voit passer.

    Incident du 2026-09-15. `citext` a ete ajoutee a `azure.extensions` par
    `az postgres flexible-server parameter set`. Le `terraform apply` suivant a retabli
    `uuid-ossp,unaccent` — la valeur du module — QUELQUES MINUTES avant que le job de migration
    Twenty ne tourne. La migration a echoue une seconde fois pour exactement la meme cause,
    apres qu'elle eut ete « corrigee ». ~40 minutes et un cycle de migration.
    """
    v = verdict(commande)
    assert v is not None, f"non attrape : {commande}"
    assert v[0] == "deny"
    assert "terraform" in v[1].lower(), "le motif doit nommer la cause, pas dire « interdit »"


def test_une_virgule_dans_command_de_containerapp_job_est_refusee(hors_main):
    """`az` ne prend qu'UNE valeur : la virgule n'est pas un separateur, et l'echec est muet.

    Incident du 2026-09-15. `az containerapp job start --command "-c","script"` : le conteneur
    demarre sans rien executer et rend `Failed` SANS UN SEUL LOG. Quatre tentatives, 1 h 30.
    Le shape fautif est la virgule ENTRE DEUX VALEURS CITEES — une liste ecrite comme en Python.
    """
    v = verdict(
        'az containerapp job start -n caj-twenty-migrate-dev -g rg-twenty-dev '
        '--command "/bin/sh","-c","yarn command:prod upgrade"'
    )
    assert v is not None, "non attrape"
    assert v[0] == "deny"
    assert "virgule" in v[1].lower()


@pytest.mark.parametrize(
    "commande",
    [
        # Lire un parametre n'ecrit rien : seul `set` entre en conflit avec Terraform.
        "az postgres flexible-server parameter show -n azure.extensions -g rg-x -s srv-x",
        "az postgres flexible-server parameter list -g rg-x -s srv-x -o json",
        # UNE valeur, meme si elle contient une virgule a l'interieur des memes guillemets.
        'az containerapp job start -n caj-x -g rg-x --command "/bin/sh -c \'echo a,b\'"',
        # Un `start` sans `--command` n'a aucun moyen de porter le defaut.
        "az containerapp job start -n caj-twenty-migrate-dev -g rg-twenty-dev",
        # Une autre commande `az` qui porte une liste separee par des virgules, legitimement.
        'az containerapp job start -n caj-x -g rg-x --env-vars "A=1,B=2"',
    ],
)
def test_les_commandes_az_legitimes_passent_toujours(commande, hors_main):
    """Un faux positif coute plus cher que le piege qu'il couvre : il apprend a contourner."""
    assert verdict(commande) is None, f"faux positif : {commande}"


# --- quatrieme faux positif du garde-fou (2026-09-16) ----------------------------------------

@pytest.mark.parametrize(
    "commande",
    [
        # L'incident : creer la PR du hook de session Azure. `az` est DANS LE TITRE.
        'gh pr create --title "garder la session az vivante, y compris en cours de sequence" '
        "--body-file corps.md | tail -2",
        # Meme forme, sur un message de commit.
        'git commit -m "documenter az login dans le runbook" | head -3',
        # Et sur une simple recherche de texte.
        "grep -rn 'az account show' docs/ | head -20",
        # La regle soeur portait le meme defaut : elle est resserree du meme geste.
        'git commit -m "toujours lire gh pr checks ligne par ligne" | head -3',
    ],
)
def test_le_mot_az_dans_un_argument_n_est_pas_une_commande_az(commande, hors_main):
    """Rencontre le 2026-09-16 : `\\baz\\b` matche « la session az vivante » dans un titre de PR.

    Le garde-fou a refuse la creation de la pull request qui livrait precisement le hook de
    session Azure. Quatrieme faux positif de la famille — les trois premiers (14/08, 17/08,
    30/08) ont chacun leur test plus haut.

    La cause est la meme a chaque fois : une regle qui lit ce que la commande TRANSPORTE au lieu
    de ce qu'elle FAIT. `_sans_corps_heredoc` traite deja le cas du heredoc ; celui-ci est un
    argument cite ordinaire. Le discriminant retenu est la POSITION : une commande commence une
    ligne ou suit un separateur (`;`, `&&`, `||`, `|`, `(`), jamais une simple espace.

    ⚠️ Volontairement etroit. `REQUESTS_CA_BUNDLE=... az account show` n'est plus vu — un
    prefixe de variable d'environnement n'est pas un separateur. C'est le bon sens du compromis :
    un refus manque coute un pipe tronquant de plus, un refus a tort apprend a contourner le
    garde-fou.
    """
    assert verdict(commande) is None, f"faux positif : {commande}"


@pytest.mark.parametrize(
    "commande",
    [
        "az containerapp job execution list -n caj-pim-migrate-dev | tail -5",
        "cd \"C:/Users/x/depot\" && az acr task list-runs --registry acrx | head -3",
        "terraform plan ; az account show | tail -1",
        "$(az account show) | head -2",
    ],
)
def test_un_vrai_az_en_position_de_commande_reste_refuse(commande, hors_main):
    """La moitie qui compte autant : resserrer ne doit pas desarmer."""
    v = verdict(commande)
    assert v is not None, f"non attrape : {commande}"
    assert v[0] == "deny"
