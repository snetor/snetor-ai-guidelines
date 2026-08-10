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
IGNORED_DIRS = {"node_modules", "venv"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def est_ignore(rel: Path) -> bool:
    """Vrai si un composant du chemin est masque (prefixe par un point) ou technique.

    La regle du point couvre `.git`, `.venv`, `.pytest_cache`, `.terraform`,
    et surtout `.docs-standard` : le workflow reutilisable
    `.github/workflows/check-docs.yml` y depose un second checkout de ce repo
    dans le repo appelant. Sans cette exclusion, les markdown du standard
    entrent dans l index attendu du repo appelant, et un repo conforme sort
    en 1 en CI alors qu il sort en 0 en local. Une regle generale valant pour
    tout dossier masque, plutot qu un nom litteral, ferme aussi le piege pour
    le prochain sous-checkout.
    """
    return any(part.startswith(".") or part in IGNORED_DIRS for part in rel.parts)


def strip_code(text: str) -> str:
    """Retire les blocs et spans de code pour ne pas y chercher de liens."""
    lines: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        # `lstrip` : une cloture indentee — bloc de code sous un item de liste,
        # sous une citation — ferme bien le bloc. Sans cela, tout le reste du
        # fichier passe pour du code, ou pire, le contenu du bloc passe pour du
        # texte et ses liens d exemple sont signales comme morts.
        if line.lstrip().startswith("```"):
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
    """Parcourt les markdown du repo en ignorant masques et dossiers techniques."""
    for chemin in sorted(repo_root.rglob("*.md")):
        if est_ignore(chemin.relative_to(repo_root)):
            continue
        yield chemin


def read_text_safe(chemin: Path) -> tuple[str | None, str | None]:
    """Lit un fichier texte en UTF-8 sans jamais lever.

    Retourne (contenu, erreur). En cas d echec de lecture — encodage
    invalide, fichier disparu entre le parcours et la lecture, verrouille
    ou inaccessible — contenu vaut None et erreur decrit la cause ; a
    l appelant de l integrer a sa propre liste d erreurs de validation.
    """
    try:
        return chemin.read_text(encoding="utf-8"), None
    except (UnicodeDecodeError, OSError) as exc:
        return None, f"lecture impossible ({exc})"


def check_links(repo_root: Path) -> list[str]:
    """Signale tout lien markdown interne pointant un fichier inexistant."""
    errors: list[str] = []
    for chemin in iter_markdown(repo_root):
        rel = chemin.relative_to(repo_root).as_posix()
        contenu, erreur = read_text_safe(chemin)
        if erreur is not None:
            errors.append(f"{rel}: {erreur}")
            continue
        texte = strip_code(contenu)
        for cible in find_internal_links(texte):
            if not (chemin.parent / cible).exists():
                errors.append(f"{rel}: lien interne mort vers {cible}")
    return errors


INDEX_MARKER = (
    "<!-- GENERATED — ne pas éditer. "
    "Régénérer via: python scripts/check_docs.py --fix -->"
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
            contenu, erreur = read_text_safe(chemin)
            if erreur is not None:
                errors.append(f"{rel}: {erreur}")
                continue
            meta, body = parse_frontmatter(contenu)
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
        contenu, erreur = read_text_safe(chemin)
        if erreur is not None:
            # Illisible : deja signale comme erreur bloquante par check_links,
            # qui parcourt le meme fichier. Pas d entree d index a construire.
            continue
        _, body = parse_frontmatter(contenu)
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
        "Généré depuis les frontmatters de `docs/live/` et `docs/dated/`. "
        "Toute modification manuelle sera écrasée."
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
            lignes.append("### À jour")
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
            lignes.append("### Datés")
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


HANDOFF_MAX_LINES = 150
SPEC_MAX_AGE_DAYS = 30
PENDING_MAX_AGE_DAYS = 90
PENDING_STATUSES = {"draft", "proposed"}
ALLOWED_DOCS_PREFIXES = ("docs/live/", "docs/dated/", "docs/superpowers/")
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def check_handoff(repo_root: Path) -> list[str]:
    """HANDOFF.md doit exister et tenir sous le plafond."""
    chemin = repo_root / "HANDOFF.md"
    if not chemin.is_file():
        return [
            "HANDOFF.md absent a la racine : le routeur d etat est obligatoire"
        ]
    contenu, erreur = read_text_safe(chemin)
    if erreur is not None:
        return [f"HANDOFF.md: {erreur}"]
    nb = len(contenu.splitlines())
    if nb > HANDOFF_MAX_LINES:
        return [
            f"HANDOFF.md fait {nb} lignes, plafond {HANDOFF_MAX_LINES} : "
            "deplacer le contenu vers docs/live/ ou docs/dated/"
        ]
    return []


def check_docs_layout(repo_root: Path) -> list[str]:
    """Interdit tout markdown dans docs/ hors des emplacements prevus."""
    errors: list[str] = []
    racine = repo_root / "docs"
    if not racine.is_dir():
        return errors
    for chemin in sorted(racine.rglob("*.md")):
        rel = chemin.relative_to(repo_root).as_posix()
        if rel == "docs/README.md" or rel.startswith(ALLOWED_DOCS_PREFIXES):
            continue
        errors.append(
            f"{rel}: emplacement interdit, attendu docs/live/, docs/dated/ "
            "ou docs/superpowers/"
        )
    return errors


def check_stale_specs(repo_root: Path, today: datetime.date) -> list[str]:
    """Une spec de la zone de travail plus vieille que le seuil bloque."""
    errors: list[str] = []
    racine = repo_root / "docs" / "superpowers" / "specs"
    if not racine.is_dir():
        return errors
    for chemin in sorted(racine.glob("*.md")):
        match = DATE_PREFIX_RE.match(chemin.name)
        if not match:
            continue
        jour = as_date(match.group(1))
        if jour is None:
            continue
        age = (today - jour).days
        if age > SPEC_MAX_AGE_DAYS:
            rel = chemin.relative_to(repo_root).as_posix()
            errors.append(
                f"{rel}: spec de {age} jours dans la zone de travail "
                f"(seuil {SPEC_MAX_AGE_DAYS}) : cloturer la branche ou "
                "reecrire la spec en docs/dated/"
            )
    return errors


def check_index(repo_root: Path, attendu: str, fix: bool) -> list[str]:
    """Compare docs/README.md au rendu attendu, ou le reecrit si fix."""
    chemin = repo_root / "docs" / "README.md"
    if chemin.is_file():
        actuel, erreur = read_text_safe(chemin)
        if erreur is not None:
            return [f"docs/README.md: {erreur}"]
    else:
        actuel = None
    if actuel == attendu:
        return []
    if fix:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(attendu, encoding="utf-8")
        return []
    return [
        "docs/README.md n est pas a jour : regenerer via "
        "python scripts/check_docs.py --fix"
    ]


def freshness_warnings(entries: list[dict], today: datetime.date) -> list[str]:
    """Warnings de fraicheur : live perime, dated en attente trop longtemps."""
    warnings: list[str] = []
    for entree in entries:
        meta = entree["meta"]
        if meta["regime"] == "live":
            revu = as_date(meta.get("reviewed"))
            if revu is None:
                continue
            jours = int(str(meta.get("ttl", DEFAULT_TTL)).rstrip("d"))
            if (today - revu).days > jours:
                warnings.append(
                    f"{entree['rel']}: revu le {revu}, ttl {jours}d depasse : "
                    "relire et mettre a jour reviewed"
                )
        elif meta.get("status") in PENDING_STATUSES:
            jour = as_date(meta.get("date"))
            if jour is None:
                continue
            age = (today - jour).days
            if age > PENDING_MAX_AGE_DAYS:
                warnings.append(
                    f"{entree['rel']}: status {meta['status']} depuis {age} "
                    "jours : trancher ou passer en superseded"
                )
    return warnings


def run(
    repo_root: Path, fix: bool, today: datetime.date
) -> tuple[list[str], list[str]]:
    """Execute tous les checks. Retourne (erreurs bloquantes, warnings)."""
    entries, errors = collect_entries(repo_root)
    attendu = generate_index(entries, find_side_readmes(repo_root))
    errors += check_index(repo_root, attendu, fix)
    errors += check_links(repo_root)
    errors += check_handoff(repo_root)
    errors += check_docs_layout(repo_root)
    errors += check_stale_specs(repo_root, today)
    return errors, freshness_warnings(entries, today)


def main(argv=None) -> int:
    import argparse

    parseur = argparse.ArgumentParser(
        description="Verifie le standard de documentation Snetor."
    )
    parseur.add_argument(
        "--repo-root", default=".", help="racine du repo a verifier"
    )
    parseur.add_argument(
        "--fix", action="store_true", help="regenere docs/README.md"
    )
    parseur.add_argument(
        "--today", default=None, help="date de reference ISO (tests)"
    )
    args = parseur.parse_args(argv)

    # Une valeur --today invalide ne doit jamais retomber en silence sur la date
    # du jour : sur un gate CI, une faute de frappe changerait le verdict du
    # check de specs perimees sans que personne ne le voie.
    if args.today is None:
        today = datetime.date.today()
    else:
        today = as_date(args.today)
        if today is None:
            print(
                f"ERROR --today {args.today!r} n est pas une date ISO "
                "(YYYY-MM-DD) : verdict impossible a calculer"
            )
            return 2

    errors, warnings = run(Path(args.repo_root).resolve(), args.fix, today)

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")

    if errors:
        print(f"\n{len(errors)} erreur(s) bloquante(s), {len(warnings)} warning(s).")
        return 1
    print(f"OK — 0 erreur, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
