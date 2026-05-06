<div align="center">
  <img src="assets/snetor_full_logo.png" alt="Snetor" height="56" />
  <br /><br />
  <p><strong>AI ENGINEERING GUIDELINES</strong></p>
  <p>Configurations, workflows et bonnes pratiques Claude Code pour les AI Engineers Snetor.</p>
  <br />
  <img src="https://img.shields.io/badge/Claude_Code-007D36?style=flat-square&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Superpowers-152B47?style=flat-square&logoColor=white" alt="Superpowers" />
  <img src="https://img.shields.io/badge/Context7-168C74?style=flat-square&logoColor=white" alt="Context7" />
  <img src="https://img.shields.io/badge/Node.js_18+-1E1B2F?style=flat-square&logoColor=white" alt="Node.js" />
</div>

---

## CONTENU DU REPO

| Fichier / Dossier | Description |
|---|---|
| `CLAUDE.md` | Instructions globales injectées dans chaque session Claude Code |
| `statusline/` | Status line personnalisée — contexte, rate limit, branche git |
| `assets/` | Ressources graphiques Snetor |

---

## INSTALLATION

### Prérequis

- [Claude Code](https://claude.ai/code) installé (CLI ou application desktop)
- Node.js 18+

---

### Plugin snetor-html-slides

#### Via le marketplace (recommandé)

```
/plugin marketplace add snetor/snetor-ai-guidelines
/plugin install snetor-html-slides@snetor-ai-guidelines
```

#### Manuellement

```bash
git clone https://github.com/snetor/snetor-ai-guidelines.git
```

Puis dans Claude Code : `/plugin install` et sélectionner `plugins/snetor-html-slides`.

---

### Status line

Affiche modèle actif, branche git, contexte et quota tokens en bas de terminal :

```
Claude Sonnet 4.6 | ~/dev/mon-projet | git:main | ctx ████████░░ 67% (670k/1M tok) | 5h ████░░ 40%
```

**Installation automatique (Windows) :**

```powershell
.\statusline\install.ps1
```

Redémarre Claude Code — la status line est active.

> Voir [`statusline/README.md`](statusline/README.md) pour les détails et les variantes Linux/macOS.

---

### CLAUDE.md global

Pour appliquer les conventions Snetor à tous tes projets :

```powershell
Copy-Item CLAUDE.md "$env:USERPROFILE\.claude\CLAUDE.md"
```

---

## PLUGINS RECOMMANDÉS

Activer via `/config` dans Claude Code ou directement dans `~/.claude/settings.json`.

| Plugin | Rôle |
|---|---|
| `superpowers@claude-plugins-official` | Workflows avancés — brainstorming, TDD, debugging, plans, code review |
| `context7@claude-plugins-official` | Documentation à jour des librairies, injectée directement dans le contexte |
| `frontend-design@claude-plugins-official` | Génération d'interfaces frontend de qualité production |

---

## CONFIGURATION SETTINGS.JSON

Bloc de référence pour `~/.claude/settings.json` :

```json
{
  "theme": "dark",
  "effortLevel": "medium",
  "enabledPlugins": {
    "superpowers@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true,
    "snetor-html-slides@snetor-ai-guidelines": true
  }
}
```

> La clé `statusLine` est injectée automatiquement par `.\statusline\install.ps1`.

> **Windows uniquement.** Si Git Bash n'est pas dans le PATH système, ajouter :
> ```json
> "env": { "CLAUDE_CODE_GIT_BASH_PATH": "C:\\...\\Git\\bin\\bash.exe" }
> ```

---

## WORKFLOWS

Les workflows sont gérés par le plugin `superpowers`. Chaque skill s'active automatiquement selon le contexte — aucune commande manuelle requise.

| Skill | Déclenchement | Rôle |
|---|---|---|
| `superpowers:brainstorming` | Avant toute création de feature | Explore les besoins et le design avant le code |
| `superpowers:writing-plans` | Tâche multi-étapes | Génère un plan détaillé avant l'implémentation |
| `superpowers:executing-plans` | Exécution d'un plan existant | Avancement avec checkpoints de review |
| `superpowers:test-driven-development` | Avant d'écrire du code | Cycle red-green-refactor |
| `superpowers:systematic-debugging` | Face à un bug | Diagnostic structuré avant correction |
| `superpowers:requesting-code-review` | Après implémentation | Review multi-agents |
| `superpowers:verification-before-completion` | Avant de déclarer done | Vérifie le fonctionnement réel avant commit |

---

## CONVENTIONS

### Workflow standard

1. **Plan d'abord.** Pour toute tâche non triviale (3 étapes ou plus), écrire le plan dans `tasks/todo.md` avant de toucher au code.
2. **Vérification avant done.** Ne jamais marquer une tâche complète sans preuve de fonctionnement.
3. **Subagents pour la recherche.** Déléguer l'exploration et l'analyse parallèle à des agents dédiés.
4. **Leçons.** Après toute correction, documenter le pattern dans `tasks/lessons.md`.

### Modèles Claude

| Modèle | ID | Usage recommandé |
|---|---|---|
| Claude Opus 4.7 | `claude-opus-4-7` | Tâches complexes, décisions d'architecture |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Usage quotidien (défaut) |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Tâches simples, volume élevé, latence critique |

Changer de modèle en session : `/model`

---

## RESSOURCES

- [Claude Code — Documentation officielle](https://docs.anthropic.com/claude/claude-code)
- [Anthropic API](https://docs.anthropic.com/claude/api)
- [Plugins officiels Claude Code](https://claude.ai/plugins)

---

<div align="center">
  <img src="assets/snetor_globe.png" alt="Snetor" height="32" />
  <br />
  <sub>Snetor Group — distributing polymers across 60+ countries since 1989.</sub>
</div>
