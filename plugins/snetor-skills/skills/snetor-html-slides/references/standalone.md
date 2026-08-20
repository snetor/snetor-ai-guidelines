# Snetor HTML Slides — Mode stand-alone (hors ligne)

Un deck Snetor charge par défaut trois choses depuis Internet : la police **Raleway** (Google Fonts),
les icônes **Phosphor**, et si besoin **Chart.js** / **jsvectormap**. Dans un contexte hors ligne,
tout ça tombe : le deck s'affiche en police système, sans icônes, et les charts restent vides.

Ce document décrit comment produire un deck qui **ne dépend d'aucun réseau**.

---

## 1. Quand basculer en stand-alone

Basculer dès que l'une de ces conditions est vraie :

- le collaborateur emploie les mots **stand-alone**, **autonome**, **hors ligne**, **offline**,
  **sans internet**, **package**, ou demande un deck **à envoyer par mail** ;
- le deck sera présenté chez un **client / fournisseur** ou dans une salle dont le Wi-Fi n'est pas garanti ;
- le deck doit être **archivé** et rester lisible dans plusieurs années (les CDN bougent, les URL meurent) ;
- le deck sort du périmètre Snetor (partage externe, annexe d'un appel d'offres).

En cas de doute, poser la question au Step 1 du wizard (voir `SKILL.md`, question 5).

> **Un deck de séance en salle Snetor n'a pas besoin du mode stand-alone.** Ne pas l'activer par
> défaut : il coûte un dossier d'assets plus lourd et il interdit les charts Chart.js.

---

## 2. Deux niveaux

| Niveau | Ce que c'est | Quand |
|---|---|---|
| **N1 — package autonome** *(défaut)* | 1 fichier `.html` + un dossier `assets/` **adjacent**. Zéro appel réseau. Se copie/se zippe d'un bloc. | Cas courant. Présentation hors ligne, archivage. |
| **N2 — fichier unique** | Tout est encodé en `base64` **dans** le HTML. Un seul fichier, rien autour. | Envoi par mail, dépôt dans un outil qui n'accepte qu'un fichier. |

**N1 est le défaut.** Ne passer en N2 que si le collaborateur demande explicitement *un seul fichier*.
N2 gonfle le HTML d'environ +33 % du poids des assets (les 4 polices seules pèsent ~740 ko en base64) :
au-delà de ~5 Mo, le fichier devient pénible à ouvrir et à envoyer.

---

## 3. Chemins d'assets

En stand-alone, le dossier d'assets est **adjacent au HTML**, pas dans le `03-Outputs/assets/` partagé.
Le deck et ses assets forment un couple qui se déplace ensemble.

```
03-Outputs/<dossier>/
├── 2026-07-23 - Mon deck - Audience.html
└── assets/
    └── <deck-slug>/
        ├── snetor_full_logo.png
        ├── snetor_full_logo_reversed.png
        ├── Hero-banner-abstrait.jpg
        └── Raleway-*.ttf
```

Dans le CSS, les chemins deviennent donc `assets/<deck-slug>/…` (et non `../assets/<deck-slug>/…`) :

```css
--logo: url("assets/<deck-slug>/snetor_full_logo.png");
--logo-reversed: url("assets/<deck-slug>/snetor_full_logo_reversed.png");
--hero: url("assets/<deck-slug>/Hero-banner-abstrait.jpg");
```

---

## 4. Polices — remplacer Google Fonts

**Supprimer** les trois `<link>` Google Fonts du `<head>`. **Copier** les quatre fichiers depuis
`assets/fonts/` du skill vers le dossier d'assets du deck, et **déclarer** les `@font-face` en tête du
bloc `<style>`, avant les `:root` :

```css
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Regular.ttf")  format("truetype"); font-weight:400; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Medium.ttf")   format("truetype"); font-weight:500; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-SemiBold.ttf") format("truetype"); font-weight:600; font-display:swap; }
@font-face { font-family:"Raleway"; src:url("assets/<deck-slug>/Raleway-Bold.ttf")     format("truetype"); font-weight:700; font-display:swap; }
```

Le reste du CSS est inchangé : `font-family: "Raleway", system-ui, …` continue de fonctionner.

> **Piège vérifié** : ne jamais retirer le `<link>` Google Fonts sans avoir posé les `@font-face`.
> Le deck bascule silencieusement en police système et personne ne le voit avant la séance.

---

## 5. Icônes — remplacer Phosphor

Le CDN Phosphor est interdit en stand-alone. Deux stratégies, dans l'ordre de préférence :

**A. Se passer d'icônes** *(recommandé)*. Les composants du design system (`fact-card`, `card`,
`brick`, `phase`…) sont conçus pour fonctionner sans icône : un chiffre, un titre, une phrase suffisent.
Un deck aéré perd peu à ne pas avoir d'icônes.

**B. SVG inline.** Si une iconographie est indispensable, embarquer les SVG directement dans le markup.
Garder la classe `ph-icon` pour hériter du cadre et des tons (`.navy`, `.teal`, dark-safe) :

```html
<span class="ph-icon" aria-hidden="true">
  <svg viewBox="0 0 256 256" width="32" height="32" fill="currentColor">
    <path d="M128 24a104 104 0 1 0 104 104A104.1 104.1 0 0 0 128 24Z"/>
  </svg>
</span>
```

Récupérer les tracés sur <https://phosphoricons.com> (MIT) au moment de la génération, un par icône
réellement utilisée. Ne pas embarquer une police d'icônes entière pour trois pictos.

---

## 6. Charts — sans CDN

**Par défaut : ne pas utiliser Chart.js en stand-alone.** Le design system fournit des visuels
purement CSS qui couvrent l'essentiel des besoins, et qui sont de toute façon la forme préférée
pour un deck aéré (cf. règle 28 « densité par défaut ») :

| Besoin | Composant CSS |
|---|---|
| Répartition en une barre | `.stacked` + `.legend` |
| Comparaison de quelques valeurs | `.impact-bars` |
| Coût / TCO exécutif | `macro cost-code` |
| Un chiffre fort | `big-number` |
| 4 métriques | `market-facts` / `fact-card` |
| Séquence, jalons | `path`, `timeline`, `gantt`, `journey` |

**Si un chart Chart.js est réellement indispensable** (deep-dive, radar, matrice bulles) :
télécharger `chart.umd.min.js` dans le dossier d'assets du deck et le référencer en local.

```html
<script src="assets/<deck-slug>/chart.umd.min.js"></script>
```

Le bootstrap et le lazy-init de `references/charts.md` restent identiques — y compris la règle 22
(construire dans `requestAnimationFrame` à l'activation de la slide). **jsvectormap / world-map n'est
pas supporté en stand-alone** : le fond de carte se charge depuis le réseau. Remplacer par une liste
de pays ou une `market-strip`.

---

## 7. Niveau 2 — fichier unique (base64)

Uniquement sur demande explicite. Encoder chaque asset et l'inliner :

```css
@font-face { font-family:"Raleway"; src:url("data:font/ttf;base64,AAEAAA…") format("truetype"); font-weight:400; }
:root { --logo: url("data:image/png;base64,iVBORw0…"); }
```

Encodage (PowerShell) :

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("chemin\vers\asset.png")) | Set-Clipboard
```

Contraintes à respecter :
- images en `data:image/png;base64,` / `data:image/jpeg;base64,` ;
- polices en `data:font/ttf;base64,` ;
- **compresser le hero** avant encodage (une bannière en 1920px suffit) ;
- annoncer le poids final au collaborateur — au-delà de ~5 Mo, proposer de revenir en N1.

---

## 8. Vérification obligatoire

Un deck stand-alone se vérifie, il ne se suppose pas. Trois contrôles, dans l'ordre :

**1. Aucune référence réseau restante.**

```powershell
Select-String -Path "<deck>.html" -Pattern "https?://" |
  Where-Object { $_.Line -notmatch 'rel="noreferrer"' }
```

Seuls les liens `href` cliquables vers des applications internes sont acceptables — ils sont
volontaires et ne bloquent pas le rendu. Toute occurrence dans `<link>`, `<script src>`,
`@import` ou `url()` est un défaut.

**2. Chaque asset référencé existe sur le disque.**

```powershell
$html = "<deck>.html"; $dir = Split-Path $html
Select-String -Path $html -Pattern 'assets/[A-Za-z0-9._/-]+' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Sort-Object -Unique |
  ForEach-Object { if (Test-Path (Join-Path $dir $_)) { "OK   $_" } else { "MANQUANT $_" } }
```

**3. Rendu réel, réseau coupé.** Ouvrir le deck sous Edge et contrôler visuellement : la police doit
être Raleway (et non une police système), le logo et le hero doivent s'afficher. En headless :

```powershell
& $edge --headless=new --disable-gpu --window-size=1600,1000 --virtual-time-budget=4000 `
        --screenshot="out.png" "file:///…/<deck>.html?slide=1"
```

> Le contrôle 3 n'est pas optionnel : les contrôles 1 et 2 ne détectent pas une police mal déclarée.

---

## 9. Récapitulatif des écarts au mode normal

| Règle `SKILL.md` | Mode normal | Mode stand-alone |
|---|---|---|
| Google Fonts | 3 `<link>` dans le `<head>` | supprimés, remplacés par 4 `@font-face` |
| 13 — CDN libs | Chart.js / jsvectormap via CDN | interdit ; Chart.js vendoré si indispensable, jsvectormap non supporté |
| 19 — Phosphor | `<i class="ph ph-…">` via CDN | pas d'icônes, ou SVG inline |
| Step 3 — chemins | `../assets/<deck-slug>/` | `assets/<deck-slug>/` adjacent au HTML |
| 22 — lazy-init charts | inchangée | inchangée (si Chart.js vendoré) |

Toutes les autres règles s'appliquent sans changement.
