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


def test_strip_code_bloc1_jamais_ferme_ne_mange_pas_lien_reel():
    # Cas du bug: deux blocs. Vieille regex apparie ``` 1 avec ``` 2 et supprime tout entre,
    # y compris un lien qui ne devrait pas être supprimé. Nouvelle: toggle ligne par ligne.
    text = "[avant](avant.md)\n```\n[faux1](fantome1.md)\n[real](real.md)\n```\n[apres](apres.md)\n```\n[faux2](fantome2.md)\n```\n"
    nettoye = strip_code(text)
    liens = find_internal_links(nettoye)
    # Vieille regex: ``` 1 et 2 appariés, [real] supprimé (perte silencieuse)
    # Nouvelle: toggle sur chaque ```, [real] supprimé (in_fence=True entre 1-2)
    assert "avant.md" in liens, f"Expected 'avant.md' to be preserved, got {liens}"
    assert "apres.md" in liens, f"Expected 'apres.md' to be preserved, got {liens}"
    # [real] et [faux2] sont dans des blocs -> doivent être supprimés
    assert "real.md" not in liens, f"Did not expect 'real.md' in {liens}"
    assert "fantome2.md" not in liens, f"Did not expect 'fantome2.md' in {liens}"


def test_strip_code_bloc_ouvert_non_ferme_ne_mange_pas_le_lien_apres():
    text = "[reel1](reel1.md)\n```\n[faux](fantome.md)\n[reel2](reel2.md)\n"
    nettoye = strip_code(text)
    assert find_internal_links(nettoye) == ["reel1.md"]


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
