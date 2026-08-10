"""Verificateur du standard de documentation Snetor.

Voir docs/live/documentation-standard.md pour la doctrine.
Sort en code 1 si au moins une erreur bloquante est detectee, 0 sinon.
Les warnings n affectent jamais le code de sortie.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

import yaml

REGIMES = {"live", "dated"}
AUDIENCES = {"agent", "dev", "newcomer", "ops", "business"}
STATUSES = {"draft", "proposed", "decided", "applied", "superseded"}
DEFAULT_TTL = "90d"

TTL_RE = re.compile(r"^\d+d$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Extrait le frontmatter YAML en tete de fichier.

    Retourne (meta, corps). meta vaut None si le fichier ne commence pas par
    un bloc `---` correctement ferme, ou si le YAML n est pas un mapping.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None, text
    if not isinstance(meta, dict):
        return None, text
    return meta, text[match.end() :]


def as_date(value) -> datetime.date | None:
    """Normalise une valeur de frontmatter en date. None si non convertible."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def validate_frontmatter(
    meta: dict | None, rel_path: str, repo_root: Path
) -> list[str]:
    """Valide le frontmatter d un fichier de docs/live/ ou docs/dated/."""
    if meta is None:
        return [f"{rel_path}: frontmatter absent ou invalide"]

    errors: list[str] = []
    posix = rel_path.replace("\\", "/")

    regime = meta.get("regime")
    if not isinstance(regime, str) or regime not in REGIMES:
        errors.append(
            f"{rel_path}: regime absent ou invalide ({regime!r}), attendu "
            f"{sorted(REGIMES)}"
        )
    else:
        expected = "live" if posix.startswith("docs/live/") else "dated"
        if regime != expected:
            errors.append(
                f"{rel_path}: regime {regime!r} incoherent avec l emplacement "
                f"docs/{expected}/, attendu {expected!r}"
            )

    audience = meta.get("audience")
    if not isinstance(audience, list) or not audience:
        errors.append(f"{rel_path}: audience doit etre une liste non vide")
    else:
        inconnues = []
        for valeur in audience:
            connue = isinstance(valeur, str) and valeur in AUDIENCES
            if not connue and valeur not in inconnues:
                inconnues.append(valeur)
        if inconnues:
            errors.append(
                f"{rel_path}: audience inconnue {sorted(inconnues, key=repr)}, attendu "
                f"parmi {sorted(AUDIENCES)}"
            )

    if regime == "live":
        if as_date(meta.get("reviewed")) is None:
            errors.append(
                f"{rel_path}: reviewed absent ou pas une date ISO (YYYY-MM-DD)"
            )
        ttl = meta.get("ttl", DEFAULT_TTL)
        if not isinstance(ttl, str) or not TTL_RE.match(ttl):
            errors.append(f"{rel_path}: ttl {ttl!r} invalide, format attendu <n>d")

    if regime == "dated":
        if as_date(meta.get("date")) is None:
            errors.append(f"{rel_path}: date absente ou pas une date ISO (YYYY-MM-DD)")
        status = meta.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(
                f"{rel_path}: status absent ou invalide ({status!r}), attendu "
                f"{sorted(STATUSES)}"
            )
        if status == "superseded" and not meta.get("superseded_by"):
            errors.append(
                f"{rel_path}: superseded_by requis quand status vaut superseded"
            )

    for champ in ("supersedes", "superseded_by"):
        cible = meta.get(champ)
        if cible and not (repo_root / str(cible)).exists():
            errors.append(f"{rel_path}: {champ} pointe un fichier inexistant ({cible})")

    return errors


SPAN_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def strip_code(text: str) -> str:
    """Retire les blocs et spans de code pour ne pas y chercher de liens."""
    lines: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(SPAN_RE.sub("", line))
    return "\n".join(lines)


def find_internal_links(text: str) -> list[str]:
    """Liste les cibles de liens markdown internes, ancre retiree."""
    cibles: list[str] = []
    for brut in LINK_RE.findall(text):
        if brut.startswith(EXTERNAL_PREFIXES):
            continue
        cible = brut.split("#", 1)[0].strip()
        if cible:
            cibles.append(cible)
    return cibles


def iter_markdown(repo_root: Path):
    """Parcourt les markdown du repo en ignorant les dossiers techniques."""
    for chemin in sorted(repo_root.rglob("*.md")):
        parties = set(chemin.relative_to(repo_root).parts)
        if parties & IGNORED_DIRS:
            continue
        yield chemin


def check_links(repo_root: Path) -> list[str]:
    """Signale tout lien markdown interne pointant un fichier inexistant."""
    errors: list[str] = []
    for chemin in iter_markdown(repo_root):
        rel = chemin.relative_to(repo_root).as_posix()
        texte = strip_code(chemin.read_text(encoding="utf-8"))
        for cible in find_internal_links(texte):
            if not (chemin.parent / cible).exists():
                errors.append(f"{rel}: lien interne mort vers {cible}")
    return errors


INDEX_MARKER = (
    "<!-- GENERATED — ne pas editer. "
    "Regenerer via: python scripts/check_docs.py --fix -->"
)
AUDIENCE_ORDER = ["agent", "dev", "newcomer", "ops", "business"]
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def extract_title(body: str, chemin: Path) -> str:
    """Titre = premier H1 du corps, sinon le nom du fichier sans extension."""
    match = TITLE_RE.search(body)
    return match.group(1).strip() if match else chemin.stem


def collect_entries(repo_root: Path) -> tuple[list[dict], list[str]]:
    """Lit docs/live/ et docs/dated/. Retourne (entrees valides, erreurs)."""
    entries: list[dict] = []
    errors: list[str] = []
    for sous_dossier in ("live", "dated"):
        racine = repo_root / "docs" / sous_dossier
        if not racine.is_dir():
            continue
        for chemin in sorted(racine.rglob("*.md")):
            rel = chemin.relative_to(repo_root).as_posix()
            meta, body = parse_frontmatter(chemin.read_text(encoding="utf-8"))
            fichier_errors = validate_frontmatter(meta, rel, repo_root)
            if fichier_errors:
                errors.extend(fichier_errors)
                continue
            entries.append(
                {"rel": rel, "title": extract_title(body, chemin), "meta": meta}
            )
    return entries, errors


def find_side_readmes(repo_root: Path) -> list[tuple[str, str]]:
    """READMEs situes hors de docs/, indexes sans exiger de frontmatter."""
    trouves: list[tuple[str, str]] = []
    for chemin in iter_markdown(repo_root):
        rel = chemin.relative_to(repo_root).as_posix()
        if chemin.name != "README.md" or rel == "README.md":
            continue
        if rel.startswith("docs/"):
            continue
        texte = chemin.read_text(encoding="utf-8")
        _, body = parse_frontmatter(texte)
        trouves.append((rel, extract_title(body, chemin)))
    return sorted(trouves)


def _lien_depuis_docs(rel: str) -> str:
    """Chemin relatif utilisable depuis docs/README.md."""
    return rel[len("docs/") :] if rel.startswith("docs/") else "../" + rel


def generate_index(
    entries: list[dict], side_readmes: list[tuple[str, str]]
) -> str:
    """Rend l index complet de docs/. Sortie deterministe."""
    lignes = [INDEX_MARKER, "", "# Index de la documentation", ""]
    lignes.append(
        "Genere depuis les frontmatters de `docs/live/` et `docs/dated/`. "
        "Toute modification manuelle sera ecrasee."
    )
    lignes.append("")

    for audience in AUDIENCE_ORDER:
        concernes = [e for e in entries if audience in e["meta"].get("audience", [])]
        if not concernes:
            continue
        lignes.append(f"## {audience}")
        lignes.append("")

        live = sorted(
            (e for e in concernes if e["meta"]["regime"] == "live"),
            key=lambda e: e["title"].lower(),
        )
        if live:
            lignes.append("### A jour")
            lignes.append("")
            for entree in live:
                revu = as_date(entree["meta"].get("reviewed"))
                lien = _lien_depuis_docs(entree["rel"])
                lignes.append(f"- [{entree['title']}]({lien}) — revu le {revu}")
            lignes.append("")

        dated = sorted(
            (e for e in concernes if e["meta"]["regime"] == "dated"),
            key=lambda e: (as_date(e["meta"].get("date")) or datetime.date.min),
            reverse=True,
        )
        if dated:
            lignes.append("### Date")
            lignes.append("")
            for entree in dated:
                jour = as_date(entree["meta"].get("date"))
                statut = entree["meta"].get("status")
                lien = _lien_depuis_docs(entree["rel"])
                lignes.append(f"- [{entree['title']}]({lien}) — {jour}, {statut}")
            lignes.append("")

    if side_readmes:
        lignes.append("## READMEs techniques (hors docs/)")
        lignes.append("")
        for rel, titre in side_readmes:
            lignes.append(f"- [{titre}](../{rel})")
        lignes.append("")

    return "\n".join(lignes).rstrip() + "\n"
