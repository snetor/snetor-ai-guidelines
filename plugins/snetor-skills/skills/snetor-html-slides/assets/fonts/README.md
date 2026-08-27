# Polices Raleway — mode stand-alone

Ces quatre fichiers ne servent **qu'au mode stand-alone** (`references/standalone.md`).
En mode connecté, le deck charge Raleway depuis Google Fonts et ces fichiers ne sont pas copiés.

| Fichier | Graisse | Usage dans le design system |
|---|---|---|
| `Raleway-Regular.ttf` | 400 | corps de texte (`p`, `li`, `.sources`, captions) |
| `Raleway-Medium.ttf` | 500 | sous-titres (`.lead`, `.sd-sub`), tooltips |
| `Raleway-SemiBold.ttf` | 600 | titres (`h1`, `h2`, `.statement`, `.closing-title`) |
| `Raleway-Bold.ttf` | 700 | accents, micro-labels, chiffres (`h3`, `.eyebrow`, `.metric`, `.pill`) |

Ces quatre graisses sont les **seules** que le design system autorise, en stand-alone comme en mode
connecté. Un `font-weight:800` / `900` n'a pas de fonte correspondante : le navigateur épaissit le
700 en gras synthétique et le rendu n'est plus du Raleway. Pour ajouter un ExtraBold, il faut la
fonte **et** le `800` dans l'URL Google Fonts — voir `references/css-system.md` → Échelle
typographique.

## Provenance et licence

- **Fonte** : Raleway, version `4.026`
- **Copyright** : « Copyright 2010 The Raleway Project Authors (impallari@gmail.com) »
- **Licence** : SIL Open Font License 1.1 — <https://openfontlicense.org>
- **Projet amont** : <https://github.com/impallari/Raleway>

La police est distribuée sous OFL, donc redistribuable avec le skill. La licence est **distincte
de la licence MIT du dépôt** : elle s'applique aux seuls fichiers de ce dossier.

> ⚠️ **À compléter** : l'OFL impose que le texte intégral de la licence accompagne les fichiers de
> fonte redistribués. Récupérer `OFL.txt` depuis la release officielle Raleway et le déposer ici.
> Ne pas le retranscrire de mémoire — c'est un texte juridique, il doit être copié à l'identique.

## Vérifier un fichier de fonte

```powershell
$b = [IO.File]::ReadAllBytes("Raleway-Regular.ttf")
($b[0..3] | % { $_.ToString("X2") }) -join ""            # doit valoir 00010000 (TrueType)
([Text.Encoding]::ASCII.GetString($b) -replace "\x00","") -match "Raleway"
```
