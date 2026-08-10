import datetime

from check_docs import (
    AUDIENCES,
    DEFAULT_TTL,
    REGIMES,
    STATUSES,
    as_date,
    parse_frontmatter,
    validate_frontmatter,
)


def test_parse_frontmatter_extrait_le_yaml_et_le_corps():
    text = "---\nregime: live\naudience: [dev]\n---\n# Titre\n\ncorps\n"
    meta, body = parse_frontmatter(text)
    assert meta == {"regime": "live", "audience": ["dev"]}
    assert body.startswith("# Titre")


def test_parse_frontmatter_sans_frontmatter_retourne_none():
    text = "# Titre\n\npas de frontmatter\n"
    meta, body = parse_frontmatter(text)
    assert meta is None
    assert body == text


def test_parse_frontmatter_delimiteur_de_fermeture_manquant_retourne_none():
    text = "---\nregime: live\n\n# Titre jamais ferme\n"
    meta, body = parse_frontmatter(text)
    assert meta is None


def test_parse_frontmatter_yaml_invalide_retourne_none():
    text = "---\nfoo: [1, 2\n---\n"
    meta, body = parse_frontmatter(text)
    assert meta is None


def test_parse_frontmatter_yaml_non_mapping_retourne_none():
    text = "---\n- un\n- deux\n---\n# Titre\n"
    meta, body = parse_frontmatter(text)
    assert meta is None


def test_as_date_accepte_une_date_yaml_et_une_chaine_iso():
    assert as_date(datetime.date(2026, 8, 10)) == datetime.date(2026, 8, 10)
    assert as_date("2026-08-10") == datetime.date(2026, 8, 10)
    assert as_date("10/08/2026") is None
    assert as_date(None) is None


def test_constantes_conformes_a_la_spec():
    assert REGIMES == {"live", "dated"}
    assert AUDIENCES == {"agent", "dev", "newcomer", "ops", "business"}
    assert STATUSES == {"draft", "proposed", "decided", "applied", "superseded"}
    assert DEFAULT_TTL == "90d"


def test_validate_live_valide_ne_produit_aucune_erreur(tmp_path):
    meta = {
        "regime": "live",
        "audience": ["dev", "ops"],
        "reviewed": datetime.date(2026, 8, 10),
        "ttl": "90d",
    }
    assert validate_frontmatter(meta, "docs/live/architecture.md", tmp_path) == []


def test_validate_frontmatter_absent_est_une_erreur(tmp_path):
    errors = validate_frontmatter(None, "docs/live/architecture.md", tmp_path)
    assert len(errors) == 1
    assert "frontmatter absent" in errors[0]


def test_validate_regime_incoherent_avec_le_dossier(tmp_path):
    meta = {"regime": "dated", "audience": ["dev"], "date": "2026-08-10", "status": "decided"}
    errors = validate_frontmatter(meta, "docs/live/architecture.md", tmp_path)
    assert any("regime" in e and "docs/live/" in e for e in errors)


def test_validate_audience_vide_ou_invalide(tmp_path):
    base = {"regime": "live", "reviewed": "2026-08-10"}
    assert any(
        "audience" in e
        for e in validate_frontmatter({**base, "audience": []}, "docs/live/a.md", tmp_path)
    )
    assert any(
        "audience" in e
        for e in validate_frontmatter({**base, "audience": ["boss"]}, "docs/live/a.md", tmp_path)
    )
    assert any(
        "audience" in e
        for e in validate_frontmatter({**base, "audience": "dev"}, "docs/live/a.md", tmp_path)
    )


def test_validate_live_sans_reviewed(tmp_path):
    meta = {"regime": "live", "audience": ["dev"]}
    errors = validate_frontmatter(meta, "docs/live/a.md", tmp_path)
    assert any("reviewed" in e for e in errors)


def test_validate_live_ttl_mal_forme(tmp_path):
    meta = {"regime": "live", "audience": ["dev"], "reviewed": "2026-08-10", "ttl": "3 mois"}
    errors = validate_frontmatter(meta, "docs/live/a.md", tmp_path)
    assert any("ttl" in e for e in errors)


def test_validate_dated_sans_status_ni_date(tmp_path):
    meta = {"regime": "dated", "audience": ["dev"]}
    errors = validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path)
    assert any("date" in e for e in errors)
    assert any("status" in e for e in errors)


def test_validate_dated_status_hors_enumeration(tmp_path):
    meta = {
        "regime": "dated",
        "audience": ["dev"],
        "date": "2026-08-10",
        "status": "en cours",
    }
    errors = validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path)
    assert any("status" in e for e in errors)


def test_validate_superseded_exige_superseded_by(tmp_path):
    meta = {
        "regime": "dated",
        "audience": ["dev"],
        "date": "2026-08-10",
        "status": "superseded",
    }
    errors = validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path)
    assert any("superseded_by" in e for e in errors)


def test_validate_supersedes_pointant_un_fichier_inexistant(tmp_path):
    meta = {
        "regime": "dated",
        "audience": ["dev"],
        "date": "2026-08-10",
        "status": "decided",
        "supersedes": "docs/dated/decisions/fantome.md",
    }
    errors = validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path)
    assert any("supersedes" in e and "fantome" in e for e in errors)


def test_validate_regime_non_hashable_est_une_erreur(tmp_path):
    meta = {"regime": {"live": True}, "audience": ["dev"]}
    errors = validate_frontmatter(meta, "docs/live/a.md", tmp_path)
    assert any("regime" in e for e in errors)


def test_validate_status_non_hashable_est_une_erreur(tmp_path):
    meta = {
        "regime": "dated",
        "audience": ["dev"],
        "date": "2026-08-10",
        "status": {"decided": True},
    }
    errors = validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path)
    assert any("status" in e for e in errors)


def test_validate_audience_element_non_hashable_est_une_erreur(tmp_path):
    meta = {"regime": "live", "reviewed": "2026-08-10", "audience": [{"a": 1}]}
    errors = validate_frontmatter(meta, "docs/live/a.md", tmp_path)
    assert any("audience" in e for e in errors)


def test_validate_supersedes_pointant_un_fichier_existant(tmp_path):
    cible = tmp_path / "docs" / "dated" / "decisions" / "ancien.md"
    cible.parent.mkdir(parents=True)
    cible.write_text("# ancien\n", encoding="utf-8")
    meta = {
        "regime": "dated",
        "audience": ["dev"],
        "date": "2026-08-10",
        "status": "decided",
        "supersedes": "docs/dated/decisions/ancien.md",
    }
    assert validate_frontmatter(meta, "docs/dated/decisions/a.md", tmp_path) == []


from check_docs import check_links, find_internal_links, iter_markdown, strip_code


def test_strip_code_retire_les_blocs_et_les_spans():
    text = "avant\n```\n[faux](fantome.md)\n```\napres `[aussi](fantome.md)` fin\n"
    nettoye = strip_code(text)
    assert "fantome.md" not in nettoye
    assert "avant" in nettoye
    assert "fin" in nettoye


def test_find_internal_links_ignore_http_mailto_et_ancres():
    text = (
        "[a](live/a.md) [b](https://example.com) [c](mailto:x@y.z) "
        "[d](#section) [e](../tests/README.md#titre)\n"
    )
    assert find_internal_links(text) == ["live/a.md", "../tests/README.md"]


def test_find_internal_links_ignore_ce_qui_est_dans_un_bloc_de_code():
    text = "```\n[faux](fantome.md)\n```\n[vrai](reel.md)\n"
    assert find_internal_links(strip_code(text)) == ["reel.md"]


def test_iter_markdown_ignore_git_et_node_modules(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("a", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "c.md").write_text("c", encoding="utf-8")
    trouves = sorted(p.name for p in iter_markdown(tmp_path))
    assert trouves == ["a.md"]


def test_check_links_signale_un_lien_mort_et_accepte_un_lien_valide(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "cible.md").write_text("# cible\n", encoding="utf-8")
    (tmp_path / "docs" / "source.md").write_text(
        "[ok](cible.md) et [casse](fantome.md)\n", encoding="utf-8"
    )
    errors = check_links(tmp_path)
    assert len(errors) == 1
    assert "fantome.md" in errors[0]
    assert "docs/source.md" in errors[0].replace("\\", "/")


def test_check_links_resout_relativement_au_fichier_pas_au_repo(tmp_path):
    (tmp_path / "docs" / "live").mkdir(parents=True)
    (tmp_path / "docs" / "live" / "voisin.md").write_text("# v\n", encoding="utf-8")
    (tmp_path / "docs" / "live" / "source.md").write_text(
        "[voisin](voisin.md)\n", encoding="utf-8"
    )
    assert check_links(tmp_path) == []


def test_strip_code_bloc_non_ferme_supprime_le_lien_qui_le_suit():
    # Un seul marqueur ``` (jamais referme): tout ce qui suit, jusqu a la fin
    # du fichier, est traite comme du code. Le lien qui suit le marqueur
    # d ouverture disparait donc, meme s il ressemble a un lien reel.
    text = "[reel1](reel1.md)\n```\n[faux](fantome.md)\n[reel2](reel2.md)\n"
    nettoye = strip_code(text)
    assert find_internal_links(nettoye) == ["reel1.md"]


def test_strip_code_nombre_impair_de_marqueurs_traite_la_fin_comme_code():
    # Trois marqueurs ```: le contenu situe apres le dernier marqueur non
    # apparie est traite comme etant a l interieur d un bloc de code non
    # referme (CommonMark: un bloc non ferme s etend jusqu a la fin du
    # document). Le lien qui y figure ne doit donc pas remonter.
    text = (
        "[a](a.md)\n"
        "```\n"
        "[faux1](f1.md)\n"
        "[intercale](i.md)\n"
        "```\n"
        "[faux2](f2.md)\n"
        "```\n"
        "[c](c.md)\n"
    )
    nettoye = strip_code(text)
    assert find_internal_links(nettoye) == ["a.md", "f2.md"]


def test_strip_code_bloc_avec_annotation_de_langage():
    text = "```python\n[faux](fantome.md)\n```\n[vrai](reel.md)\n"
    nettoye = strip_code(text)
    assert "fantome.md" not in nettoye
    assert find_internal_links(nettoye) == ["reel.md"]


def test_strip_code_bloc_non_ferme_en_fin_de_fichier():
    text = "[avant](avant.md)\n```\n[faux](fantome.md)\n"
    nettoye = strip_code(text)
    assert "fantome.md" not in nettoye
    assert find_internal_links(nettoye) == ["avant.md"]


from check_docs import (
    INDEX_MARKER,
    collect_entries,
    extract_title,
    find_side_readmes,
    generate_index,
)


def _ecrire(chemin, contenu):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")


def test_extract_title_prend_le_premier_titre_h1(tmp_path):
    assert extract_title("\n# Mon titre\n\ncorps\n", tmp_path / "a.md") == "Mon titre"


def test_extract_title_retombe_sur_le_nom_de_fichier(tmp_path):
    assert extract_title("pas de titre\n", tmp_path / "mon-doc.md") == "mon-doc"


def test_collect_entries_ramasse_live_et_dated_avec_erreurs(tmp_path):
    _ecrire(
        tmp_path / "docs" / "live" / "archi.md",
        "---\nregime: live\naudience: [dev]\nreviewed: 2026-08-10\n---\n# Architecture\n",
    )
    _ecrire(
        tmp_path / "docs" / "dated" / "decisions" / "2026-08-03-choix.md",
        "---\nregime: dated\naudience: [business]\ndate: 2026-08-03\nstatus: decided\n---\n# Choix\n",
    )
    _ecrire(tmp_path / "docs" / "live" / "casse.md", "# Sans frontmatter\n")
    entries, errors = collect_entries(tmp_path)
    assert sorted(e["title"] for e in entries) == ["Architecture", "Choix"]
    assert len(errors) == 1
    assert "casse.md" in errors[0]


def test_collect_entries_ignore_superpowers_et_le_readme(tmp_path):
    _ecrire(tmp_path / "docs" / "README.md", "index\n")
    _ecrire(tmp_path / "docs" / "superpowers" / "specs" / "2026-08-10-x-design.md", "spec\n")
    entries, errors = collect_entries(tmp_path)
    assert entries == []
    assert errors == []


def test_find_side_readmes_trouve_hors_docs(tmp_path):
    _ecrire(tmp_path / "tests" / "README.md", "# Tests SQL\n")
    _ecrire(tmp_path / "docs" / "live" / "README.md", "# Ignore\n")
    assert find_side_readmes(tmp_path) == [("tests/README.md", "Tests SQL")]


def test_generate_index_groupe_par_audience_et_porte_le_marqueur():
    entries = [
        {
            "rel": "docs/live/archi.md",
            "title": "Architecture",
            "meta": {
                "regime": "live",
                "audience": ["dev", "ops"],
                "reviewed": "2026-08-10",
            },
        },
        {
            "rel": "docs/dated/decisions/2026-08-03-choix.md",
            "title": "Choix",
            "meta": {
                "regime": "dated",
                "audience": ["dev"],
                "date": "2026-08-03",
                "status": "decided",
            },
        },
    ]
    sortie = generate_index(entries, [("tests/README.md", "Tests SQL")])
    assert sortie.startswith(INDEX_MARKER)
    assert "## dev" in sortie
    assert "## ops" in sortie
    assert "(live/archi.md)" in sortie
    assert "(dated/decisions/2026-08-03-choix.md)" in sortie
    assert "(../tests/README.md)" in sortie
    assert "revu le 2026-08-10" in sortie
    assert "2026-08-03, decided" in sortie
    assert sortie.index("## dev") < sortie.index("## ops")


def test_generate_index_trie_les_dated_par_date_decroissante():
    entries = [
        {
            "rel": "docs/dated/a.md",
            "title": "Ancien",
            "meta": {"regime": "dated", "audience": ["dev"], "date": "2026-06-01", "status": "decided"},
        },
        {
            "rel": "docs/dated/b.md",
            "title": "Recent",
            "meta": {"regime": "dated", "audience": ["dev"], "date": "2026-08-01", "status": "decided"},
        },
    ]
    sortie = generate_index(entries, [])
    assert sortie.index("Recent") < sortie.index("Ancien")


def test_generate_index_stable_entre_deux_appels():
    entries = [
        {
            "rel": "docs/live/a.md",
            "title": "A",
            "meta": {"regime": "live", "audience": ["dev"], "reviewed": "2026-08-10"},
        }
    ]
    assert generate_index(entries, []) == generate_index(entries, [])


from check_docs import (
    HANDOFF_MAX_LINES,
    PENDING_MAX_AGE_DAYS,
    SPEC_MAX_AGE_DAYS,
    check_docs_layout,
    check_handoff,
    check_index,
    check_stale_specs,
    freshness_warnings,
    main,
    run,
)

AUJOURD_HUI = datetime.date(2026, 8, 10)


def test_seuils_conformes_a_la_spec():
    assert HANDOFF_MAX_LINES == 150
    assert SPEC_MAX_AGE_DAYS == 30
    assert PENDING_MAX_AGE_DAYS == 90


def test_check_handoff_absent_est_une_erreur(tmp_path):
    errors = check_handoff(tmp_path)
    assert any("HANDOFF.md" in e and "absent" in e for e in errors)


def test_check_handoff_trop_long_est_une_erreur(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("ligne\n" * 151, encoding="utf-8")
    errors = check_handoff(tmp_path)
    assert any("151" in e and "150" in e for e in errors)


def test_check_handoff_dans_le_plafond_passe(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("ligne\n" * 150, encoding="utf-8")
    assert check_handoff(tmp_path) == []


def test_check_docs_layout_refuse_un_markdown_hors_des_dossiers_autorises(tmp_path):
    _ecrire(tmp_path / "docs" / "vrac.md", "# vrac\n")
    errors = check_docs_layout(tmp_path)
    assert any("docs/vrac.md" in e for e in errors)


def test_check_docs_layout_accepte_readme_live_dated_superpowers(tmp_path):
    _ecrire(tmp_path / "docs" / "README.md", "index\n")
    _ecrire(tmp_path / "docs" / "live" / "a.md", "a\n")
    _ecrire(tmp_path / "docs" / "dated" / "b.md", "b\n")
    _ecrire(tmp_path / "docs" / "superpowers" / "specs" / "c.md", "c\n")
    assert check_docs_layout(tmp_path) == []


def test_check_stale_specs_bloque_au_dela_de_30_jours(tmp_path):
    _ecrire(tmp_path / "docs" / "superpowers" / "specs" / "2026-07-01-vieille-design.md", "x\n")
    _ecrire(tmp_path / "docs" / "superpowers" / "specs" / "2026-08-05-fraiche-design.md", "x\n")
    errors = check_stale_specs(tmp_path, AUJOURD_HUI)
    assert len(errors) == 1
    assert "2026-07-01-vieille-design.md" in errors[0]


def test_check_stale_specs_ignore_un_nom_sans_date(tmp_path):
    _ecrire(tmp_path / "docs" / "superpowers" / "specs" / "notes.md", "x\n")
    assert check_stale_specs(tmp_path, AUJOURD_HUI) == []


def test_check_index_signale_une_divergence_puis_la_corrige(tmp_path):
    _ecrire(
        tmp_path / "docs" / "live" / "a.md",
        "---\nregime: live\naudience: [dev]\nreviewed: 2026-08-10\n---\n# A\n",
    )
    entries, _ = collect_entries(tmp_path)
    attendu = generate_index(entries, find_side_readmes(tmp_path))

    errors = check_index(tmp_path, attendu, fix=False)
    assert any("docs/README.md" in e for e in errors)

    assert check_index(tmp_path, attendu, fix=True) == []
    assert (tmp_path / "docs" / "README.md").read_text(encoding="utf-8") == attendu
    assert check_index(tmp_path, attendu, fix=False) == []


def test_freshness_warnings_live_perime_et_frais():
    entries = [
        {
            "rel": "docs/live/vieux.md",
            "title": "Vieux",
            "meta": {"regime": "live", "audience": ["dev"], "reviewed": "2026-01-01", "ttl": "90d"},
        },
        {
            "rel": "docs/live/frais.md",
            "title": "Frais",
            "meta": {"regime": "live", "audience": ["dev"], "reviewed": "2026-08-01"},
        },
    ]
    warnings = freshness_warnings(entries, AUJOURD_HUI)
    assert len(warnings) == 1
    assert "docs/live/vieux.md" in warnings[0]


def test_freshness_warnings_dated_en_attente_depuis_plus_de_90_jours():
    entries = [
        {
            "rel": "docs/dated/vieille-propo.md",
            "title": "Propo",
            "meta": {"regime": "dated", "audience": ["dev"], "date": "2026-01-01", "status": "proposed"},
        },
        {
            "rel": "docs/dated/tranchee.md",
            "title": "Tranchee",
            "meta": {"regime": "dated", "audience": ["dev"], "date": "2026-01-01", "status": "decided"},
        },
    ]
    warnings = freshness_warnings(entries, AUJOURD_HUI)
    assert len(warnings) == 1
    assert "vieille-propo.md" in warnings[0]


def _repo_conforme(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")
    _ecrire(
        tmp_path / "docs" / "live" / "a.md",
        "---\nregime: live\naudience: [dev]\nreviewed: 2026-08-10\n---\n# A\n",
    )
    entries, _ = collect_entries(tmp_path)
    _ecrire(
        tmp_path / "docs" / "README.md",
        generate_index(entries, find_side_readmes(tmp_path)),
    )


def test_run_sur_un_repo_conforme_ne_produit_aucune_erreur(tmp_path):
    _repo_conforme(tmp_path)
    errors, warnings = run(tmp_path, fix=False, today=AUJOURD_HUI)
    assert errors == []
    assert warnings == []


def test_main_retourne_1_si_erreur_et_0_sinon(tmp_path, capsys):
    assert main(["--repo-root", str(tmp_path)]) == 1
    capsys.readouterr()

    _repo_conforme(tmp_path)
    assert main(["--repo-root", str(tmp_path), "--today", "2026-08-10"]) == 0
    sortie = capsys.readouterr().out
    assert "OK" in sortie


def test_main_fix_regenere_l_index_et_retourne_0(tmp_path, capsys):
    (tmp_path / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")
    _ecrire(
        tmp_path / "docs" / "live" / "a.md",
        "---\nregime: live\naudience: [dev]\nreviewed: 2026-08-10\n---\n# A\n",
    )
    assert main(["--repo-root", str(tmp_path), "--today", "2026-08-10"]) == 1
    capsys.readouterr()
    assert main(["--repo-root", str(tmp_path), "--today", "2026-08-10", "--fix"]) == 0
    assert (tmp_path / "docs" / "README.md").exists()


def test_main_warning_ne_change_pas_le_code_de_sortie(tmp_path, capsys):
    (tmp_path / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")
    _ecrire(
        tmp_path / "docs" / "live" / "vieux.md",
        "---\nregime: live\naudience: [dev]\nreviewed: 2026-01-01\n---\n# Vieux\n",
    )
    assert main(["--repo-root", str(tmp_path), "--today", "2026-08-10", "--fix"]) == 0
    assert "WARN" in capsys.readouterr().out


from check_docs import read_text_safe


def test_read_text_safe_gere_l_encodage_invalide(tmp_path):
    chemin = tmp_path / "casse.md"
    chemin.write_bytes(b"\xff\xfe invalide")
    contenu, erreur = read_text_safe(chemin)
    assert contenu is None
    assert erreur is not None


def test_read_text_safe_gere_le_fichier_absent(tmp_path):
    contenu, erreur = read_text_safe(tmp_path / "absent.md")
    assert contenu is None
    assert erreur is not None


def test_lecture_non_utf8_dans_docs_live_signalee_sans_lever(tmp_path):
    _repo_conforme(tmp_path)
    (tmp_path / "docs" / "live" / "casse.md").write_bytes(b"\xff\xfe invalide")

    errors, _ = run(tmp_path, fix=False, today=AUJOURD_HUI)
    assert any("docs/live/casse.md" in e.replace("\\", "/") for e in errors)
    assert main(["--repo-root", str(tmp_path), "--today", "2026-08-10"]) == 1


def test_lecture_non_utf8_hors_docs_signalee_par_check_links(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "vieux.md").write_bytes(b"\xff\xfe invalide")

    errors = check_links(tmp_path)
    assert any("notes/vieux.md" in e.replace("\\", "/") for e in errors)


def test_lecture_non_utf8_n_empeche_pas_de_rapporter_une_autre_erreur(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "casse.md").write_bytes(b"\xff\xfe invalide")
    _ecrire(tmp_path / "docs" / "source.md", "[mort](fantome.md)\n")

    errors = check_links(tmp_path)
    assert any("casse.md" in e for e in errors)
    assert any("fantome.md" in e for e in errors)
