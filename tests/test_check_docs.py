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
