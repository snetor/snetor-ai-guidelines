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


FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
SPAN_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def strip_code(text: str) -> str:
    """Retire les blocs et spans de code pour ne pas y chercher de liens."""
    return SPAN_RE.sub("", FENCE_RE.sub("", text))


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
