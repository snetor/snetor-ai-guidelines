# deploy-claude.ps1 — Déploiement Claude DSI Snetor

Script PowerShell d'onboarding Claude pour un collaborateur Snetor.  
Une seule exécution, **une seule boite UAC**, tout le reste est automatique.

## Ce que fait le script

| Phase | Action |
|---|---|
| 0 | Auto-élévation admin (1 UAC) — profil collab préservé |
| 1 | Node.js LTS — détecte la version courante et installe silencieusement si absent |
| 2 | Git for Windows — installe le dernier release officiel (GitHub `git-for-windows`) si absent |
| 3 | Claude Desktop — MSIX officiel signé, provisioning machine-wide (`Add-AppxProvisionedPackage`) |
| 4 | Claude Code (Cowork) — `npm install -g @anthropic-ai/claude-code` dans le profil du collab |
| 5 | Config Snetor — CLAUDE.md global, settings.json (plugins), status line |
| 6 | M365 MCP — pré-configure `claude_desktop_config.json` (résolution chemin MSIX réelle) |
| 7 | Récapitulatif coloré + checklist des actions manuelles |

## Prérequis

- Windows 10/11 x64
- Windows PowerShell 5.1 (le script force TLS 1.2 et s'exécute sous `powershell.exe`)
- Connexion internet (téléchargements Node.js, Git, Claude Desktop, Claude Code)
- Credentials admin DSI (pour approuver la boite UAC)

> Git est installé automatiquement (Phase 2) s'il est absent du poste.

## Utilisation

1. **Ouvrir une session Windows avec le compte du collab** (le collab est connecté sur son PC)
2. Télécharger ce repo ou copier `deploy-claude.ps1` sur le poste
3. Ouvrir un terminal PowerShell (pas admin — le script se ré-élève tout seul)
4. Exécuter :

```powershell
.\scripts\deploy-claude.ps1
```

5. Approuver la boite UAC avec les credentials admin DSI
6. Le script tourne seul jusqu'au récapitulatif final (~5-10 min)

## Étapes manuelles post-déploiement (collab)

Ces actions nécessitent le navigateur et ne peuvent pas être automatisées :

1. **Claude Desktop** → ouvrir l'app → se connecter avec le compte `@snetor.com`
2. **Connecteur M365** → dans Claude Desktop : Paramètres → Extensions → Microsoft 365 → Autoriser
3. **Claude Code** → dans un terminal, taper `claude` → s'authentifier via le navigateur

## Action admin DSI — une seule fois pour tout le tenant

Avant que les collabs puissent autoriser le connecteur M365, l'admin Entra doit accorder le consentement :

1. Aller sur `https://entra.microsoft.com`
2. Applications d'entreprise → chercher *M365 MCP Client for Claude*
3. Cliquer **Accorder le consentement administrateur**

Cette étape est nécessaire une seule fois — elle débloque l'autorisation pour tous les utilisateurs du tenant.

## Dépannage

| Symptôme | Solution |
|---|---|
| Phase 3 ⚠️ "vérification manuelle" | Télécharger manuellement le MSIX sur `https://claude.com/download` |
| `npm` introuvable après Phase 1 | Fermer le terminal, relancer le script — Node.js s'est installé mais PATH pas encore rafraîchi |
| `claude` command non reconnue après Phase 4 | Ouvrir un nouveau terminal — PATH utilisateur mis à jour au redémarrage du shell |
| Claude Desktop absent du menu Démarrer | Provisioning machine-wide : il apparaît à la **prochaine ouverture de session Windows** du collab |
| Extensions M365 absent dans Claude Desktop | Vérifier que le compte claude.ai est sur un plan Teams/Enterprise |
| Config M365 chemin ⚠️ secours | Ouvrir Claude Desktop au moins une fois (crée le bon répertoire), puis relancer la Phase 6 manuellement |

## Notes techniques

- **Profil cible** : le script capture `$env:USERPROFILE` avant l'élévation et passe le chemin en paramètre à la session admin. Tous les writes user-profile (settings.json, CLAUDE.md, status line, M365 config) vont dans le profil du **collab**, pas de l'admin DSI.
- **PowerShell 5.1** : le script active TLS 1.2 explicitement (5.1 négocie TLS 1.0/1.1 par défaut, refusé par nodejs.org / GitHub / claude.ai) et écrit les JSON en UTF-8 **sans BOM** (le `-Encoding UTF8` natif de 5.1 ajoute un BOM qui casse les parseurs).
- **Claude Desktop (MSIX)** : installé via `Add-AppxProvisionedPackage -Online` (provisioning machine-wide). Comme le script tourne en admin élevé, un `Add-AppxPackage` per-user ne ciblerait que l'admin — le provisioning enregistre Claude pour le collab à sa prochaine ouverture de session.
- **Chemin config M365** : le MSIX lit depuis `%LOCALAPPDATA%\Packages\<PackageFamilyName>\LocalCache\Roaming\Claude\` (pas `%APPDATA%\Claude\`). Le script résout le `<PackageFamilyName>` via `Get-AppxPackage -AllUsers`, puis par dérivation depuis le package provisionné, sinon retombe sur `%APPDATA%\Claude\`.
- **npm prefix** : le prefix npm est fixé à `$TargetProfile\AppData\Roaming\npm` pour éviter que Claude Code s'installe dans le profil admin.
