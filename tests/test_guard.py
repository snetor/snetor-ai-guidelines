"""Tests du garde-fou `PreToolUse`.

Le garde-fou n'avait AUCUN test tant qu'il vivait dans `snetor-pim` : ses regressions se
decouvraient en s'y cognant, et son historique porte trois faux positifs qui ont chacun coute une
session (14/08, 17/08, 30/08). Le deployer sur quatorze depots sans harnais aurait multiplie ce
cout par quatorze.

Deux moities, egalement importantes :
  · ce qui doit etre REFUSE — la raison d'etre du garde-fou ;
  · ce qui doit PASSER — sa condition de survie. Une regle qui se declenche a tort est une regle
    desactivee dans la semaine, et un refus incomprehensible apprend a contourner le garde-fou.
"""

import guard


def denie(commande, powershell=False, cwd="."):
    """Rend le motif du refus, ou None si la commande passe."""
    verdict = guard.verifier_commande(commande, powershell, cwd)
    return verdict[1] if verdict and verdict[0] == "deny" else None


def escalade(commande, powershell=False, cwd="."):
    verdict = guard.verifier_commande(commande, powershell, cwd)
    return verdict[1] if verdict and verdict[0] == "escalate" else None


# --- pipes qui avalent le code de sortie ---------------------------------------------------

def test_gh_pr_checks_tronque_est_refuse():
    """Incident : `gh pr checks 94 | tail -4` a fait merger #95 sur du rouge."""
    assert denie("gh pr checks 94 | tail -4")
    assert denie("gh pr checks 94 | head -20")


def test_az_tronque_est_refuse():
    assert denie("az containerapp job show --name x | tail -5")


def test_powershell_select_object_compte_comme_troncature():
    assert denie("az acr repository show-tags --name x --no-logs | Select-Object -First 3", True)


def test_une_commande_qui_CITE_un_pipe_dans_un_heredoc_passe():
    """30/08 : documenter `az … | tail` dans un HANDOFF se faisait refuser.

    Le contournement etait alors d'ecrire la commande autrement — c'est-a-dire d'obeir a un
    garde-fou qui se trompait. Un garde-fou se declenche sur ce que la commande FAIT.
    """
    commande = "cat > /tmp/note.md <<'EOF'\nNe jamais faire `gh pr checks 12 | tail -4`.\nEOF"
    assert denie(commande) is None


# --- PowerShell ----------------------------------------------------------------------------

def test_set_content_accentue_est_refuse():
    """135 marqueurs mojibake commites le 07/08, apres que la lecon eut ete ecrite le 03/08."""
    assert denie('Set-Content -Path a.md -Value "clé étrangère"', True)


def test_set_content_ascii_pur_passe():
    assert denie('Set-Content -Path a.txt -Value "plain ascii"', True) is None


def test_set_content_accentue_en_bash_passe():
    """La regle vise la re-tokenisation de PowerShell, pas l'ecriture en general."""
    assert denie('Set-Content -Path a.md -Value "clé"', False) is None


def test_heredoc_en_powershell_est_refuse():
    assert denie("python - <<'PY'\nprint(1)\nPY", True)


def test_heredoc_en_bash_passe():
    assert denie("python - <<'PY'\nprint(1)\nPY", False) is None


def test_git_commit_inline_en_powershell_est_refuse():
    """PowerShell 5.1 re-tokenise : `-m \"...\"` casse au premier guillemet interne."""
    assert denie('git commit -m "feat: x"', True)


def test_select_string_avec_chevrons_ne_declenche_pas_le_heredoc():
    """L'ancre de fin de ligne epargne un motif qui n'ouvre aucun heredoc."""
    assert denie('Select-String "<<<<<<<" fichier.txt', True) is None


# --- escalades (rendues a l'humain, jamais bloquees) ----------------------------------------

def test_gh_pr_merge_remonte_a_l_humain():
    assert escalade("gh pr merge 12 --squash")


def test_git_push_force_remonte_a_l_humain():
    assert escalade("git push --force origin v1")


def test_push_force_with_lease_ne_remonte_pas():
    """`--force-with-lease` refuse d'ecraser un travail qu'on n'a pas vu : c'est la forme sure."""
    assert escalade("git push --force-with-lease origin ma-branche") is None


# --- ecritures --------------------------------------------------------------------------------

def test_ecriture_hors_du_depot_passe(tmp_path):
    """Bloc-notes, fichier temporaire, autre projet : le garde-fou n'a rien a y dire."""
    assert guard.verifier_ecriture(str(tmp_path / "note.md"), str(tmp_path / "ailleurs")) is None


def test_init_py_sous_tests_est_refuse(tmp_path):
    chemin = tmp_path / "tests" / "__init__.py"
    chemin.parent.mkdir(parents=True)
    verdict = guard.verifier_ecriture(str(chemin), str(tmp_path))
    assert verdict and verdict[0] == "deny"
    assert "pytest" in verdict[1]


def test_chemin_vide_passe():
    assert guard.verifier_ecriture("", ".") is None


# --- helpers internes -------------------------------------------------------------------------

def test_cwd_effectif_suit_un_cd_absolu(tmp_path):
    """Sans ca, le garde-fou lisait la branche du checkout PARTAGE et refusait tout worktree."""
    cible = tmp_path / "ailleurs"
    cible.mkdir()
    assert guard._cwd_effectif(f'cd "{cible}" && git commit -F m.txt', str(tmp_path)) == str(cible)


def test_cwd_effectif_retombe_sur_cwd_si_le_chemin_n_existe_pas(tmp_path):
    assert guard._cwd_effectif('cd "/nexiste/pas" && git commit', str(tmp_path)) == str(tmp_path)


def test_suppression_de_reference_n_est_pas_un_push(tmp_path):
    """17/08 : le nettoyage des branches mergees — que CLAUDE.md prescrit — etait bloque."""
    assert guard._que_des_suppressions("git push origin --delete ma-branche") is True


def test_un_vrai_push_mele_a_une_suppression_n_est_pas_exempte():
    """`all()` et non `any()` : une seule invocation qui pousse fait tomber l'exemption."""
    commande = "git push origin main; git push origin --delete vieille"
    assert guard._que_des_suppressions(commande) is False


def test_le_corps_d_un_heredoc_est_retire():
    commande = "git commit -F - <<'EOF'\nparle de git push --force\nEOF\necho fini"
    nettoye = guard._sans_corps_heredoc(commande)
    assert "--force" not in nettoye
    assert "echo fini" in nettoye


def test_un_evenement_json_illisible_ne_bloque_pas(monkeypatch, capsys):
    """Un garde-fou qui casse la session est pire que le defaut qu'il previent."""
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("pas du json"))
    assert guard.main() == 0
