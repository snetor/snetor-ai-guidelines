# Claude Code — Status Line

La status line affiche en bas de terminal : modèle actif, répertoire courant, branche git, usage de la fenêtre de contexte et limite de taux 5h.

```
Claude Sonnet 4.6 | ~/dev/mon-projet | git:main | ctx ████████░░░░ 67% (670k/1M tok) | 5h ████░░░░░░ 40%
```

## Installation

### 1. Copier le script

Choisir la variante selon votre environnement :

| Fichier | Environnement |
|---|---|
| `statusline-command.js` | **Recommandé** — Node.js (Windows, macOS, Linux) |
| `statusline-command.ps1` | PowerShell 5.1 (Windows natif) |
| `statusline-command.sh` | Bash / Git Bash / macOS / Linux |

Copier le fichier choisi dans `~/.claude/` :

**Windows (Node.js — recommandé) :**
```powershell
Copy-Item statusline-command.js "$env:USERPROFILE\.claude\statusline-command.js"
```

**macOS / Linux :**
```bash
cp statusline-command.sh ~/.claude/statusline-command.sh
chmod +x ~/.claude/statusline-command.sh
```

### 2. Configurer settings.json

Ajouter le bloc `statusLine` dans `~/.claude/settings.json` :

**Windows avec Node.js :**
```json
{
  "statusLine": {
    "type": "command",
    "command": "node C:/Users/VOTRE_USER/.claude/statusline-command.js",
    "padding": 1,
    "refreshInterval": 5
  }
}
```

**macOS / Linux avec Bash :**
```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /home/VOTRE_USER/.claude/statusline-command.sh",
    "padding": 1,
    "refreshInterval": 5
  }
}
```

**Windows avec PowerShell :**
```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -File C:/Users/VOTRE_USER/.claude/statusline-command.ps1",
    "padding": 1,
    "refreshInterval": 5
  }
}
```

> Remplacer `VOTRE_USER` par votre nom d'utilisateur système.

### 3. Vérifier

Relancer Claude Code. La status line apparaît automatiquement en bas du terminal.

## Signification des indicateurs

| Indicateur | Description |
|---|---|
| Modèle | Nom du modèle Claude actif (ex: `Claude Sonnet 4.6`) |
| Répertoire | Chemin courant abrégé (`~` = home, `…/parent/projet` si long) |
| `git:branche` | Branche git active (absent si pas de repo git) |
| `ctx` | Usage de la fenêtre de contexte — vert < 60%, orange < 85%, rouge >= 85% |
| `5h` | Quota de tokens sur 5h — bleu < 60%, orange < 85%, rouge >= 85% |
