# Artwork and source notices

Sorcery_rebirth is a modified icon pack maintained by **4oOkSk**. Raster artwork combines adapted Sorcery illustrations, public vector marks and individually prepared application artwork. Catalog tooling, the Android dashboard and packaging are modified or newly written in 2026. It is an independent continuation of Sorcery, with attribution to its original authors. GPL-2.0 covers the program and original Sorcery material; individual third-party artwork retains its own rights and licenses.

## SorceryIconPack

- Project: <https://github.com/sorcererxw/SorceryIconPack>
- Author: sorcererxw and contributors.
- License: GNU General Public License, version 2; the original license text is retained in [LICENSE](LICENSE).
- Files: `artwork/original/*.png`, `catalog/original-appfilter.xml`, and adaptations identified as original Sorcery in `catalog/icons.json`.
- Artwork is extracted from the upstream repository's published APK. Uppercase PNG extensions are normalized to lowercase; image bytes are preserved. The upstream `contracts` drawable typo is corrected to `contacts` in generated launcher metadata.
- The original app's Java code, advertising/billing integrations, fonts and native components are not included. The dashboard is implemented with Android platform APIs.

## Simple Icons

- Project: <https://github.com/simple-icons/simple-icons>
- Authors: Simple Icons contributors.
- Imported releases: 11.15.0 and 16.37.0.
- License: [CC0 1.0 Universal](licenses/Simple-Icons-CC0.md).
- Files: `artwork/glyphs/si_*.svg`; derived compositions in `artwork/icons/`.
- Imported files use CC0, including the library's default CC0 license. Files declaring other licenses are excluded. Each catalog entry records its upstream brand source and library version under `reference`.
- Changes: the symbols supply silhouettes and visual references for paper illustrations, with optical sizing, colors, layers, highlights and shadows.

## Public application artwork

Application identity references come from public Google Play, Tencent App Store and Apple App Store listings, or the application's public upstream repository. Each adapted icon records its source URL under `reference` in `catalog/icons.json`. Original marks remain the property of their respective owners; publishing this collection does not relicense those marks. Changes are paper styling, optical sizing, transparency, edge treatment and shadows, with the app's recognizable geometry preserved.

The F-Droid robot is based on the [F-Droid artwork](https://f-droid.org/assets/fdroid-logo.svg), by the F-Droid project, under [Creative Commons Attribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Its adapted PNG retains that license. The catalog identifies this exception. Telegram and Xiaomi Notes adaptations use the original Sorcery artwork under GPL-2.0.

## Application identifiers

Additional Android package and activity identifiers are extracted as factual interoperability data from [Lawnicons appfilter metadata](https://github.com/LawnchairLauncher/lawnicons/blob/develop/app/assets/appfilter.xml). Lawnicons is maintained by the Lawnchair team and contributors, under Apache-2.0. Its artwork and application implementation are not imported. The source metadata digest is recorded in `catalog/sources.json`.

Brand names and marks identify supported applications and remain the property of their respective owners. This project is independently maintained and does not imply endorsement by those owners.
