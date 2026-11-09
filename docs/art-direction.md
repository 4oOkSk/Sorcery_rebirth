# Artwork direction

New icons follow original Sorcery's vivid Material colors, clear white details, thin paper layers and directional shadows. The original pack supplies the style reference. Public application artwork supplies the mark: retain its silhouette, negative space, lettering, color relationships and arrangement.

The collection combines GPT image generation with direct adaptations of public application artwork, followed by transparent extraction and optical sizing. It is raster artwork. Compare each result against the application's actual icon; corrections belong in the PNG source and catalog entry. Authoring method, public references and the source PNG hash are recorded per icon in `catalog/icons.json`.

## Style prompt

按照参考图中原版 Sorcery 图标包的设计语言、配色、质感、立体感、阴影和视觉大小，重新设计并绘制 Android 应用图标。

请先观察原版 Sorcery 作为一个整体的视觉特征，再把新应用自然地画进同一个图标家族。让新旧图标并排时，感觉来自同一位设计师、同一套作品。

配色遵循原版：鲜明、饱满、清爽的 Material 色彩，干净的白色和明确的明暗对比。参考支付宝和 Twitter 的明亮蓝、AIDA64 的红、Evernote 和 LINE 的绿。保留各应用的识别色，白色图形保持清亮。

造型与材质：以应用实际图标为识别依据，准确保留标志轮廓、内部空白、字母笔画、颜色位置和图形之间的关系。将表面材质、薄纸层、明暗、边缘和阴影转为 Sorcery 风格。阴影自然解释叠放与折叠，保留清晰的斜向投影、轻微的边缘高光和底部阴影。图标在手机桌面尺寸下应清晰、有份量、有细节。

各图标与全部阴影完整放在自己的格子内，四边保留透明空隙。协调方形、圆形和自由轮廓的视觉份量，统一正面视角与左上方光源，输出透明 PNG。

## Source and launcher sizes

`tools/extract_sheet.py` accepts a transparent 3×3 sheet and resource names in row-major order. It removes tiny isolated fragments, preserves disconnected parts of a mark and writes 384 px sources. Square faces use approximately 152/192 of the canvas; circular and freeform shapes use approximately 176/192. Shadows remain inside the transparent canvas. Review the results at launcher size on light and dark backgrounds.

Ordinary square paper faces occupy `(40, 40, 344, 344)` in a 384 px source: both dimensions become 152 px in the APK. Measure the straight face edges rather than the full shadow bounds. For a reviewed tile with an accidentally rectangular face, run `python3 tools/normalize_tiles.py rebirth_example` to inspect the correction, then repeat with `--write`. The tool adjusts both axes and placement with the existing artwork and shadow, checks the resulting face and canvas edges, and updates the catalog hash and `generation.square_face`. Review the result visually. Select ordinary square tiles individually; books, wallets, tickets, speech bubbles and other intentional silhouettes retain their own proportions.

Square tiles use one paper outline. Extend the face color through the corners before applying that outline; an existing rounded background must not remain visible inside a second rounded mask. `repair` in `tools/repair_tile_corners.py` corrects this overlap in a 384 px tile with its 304 px face at `(40, 40, 344, 344)`. It changes the corner RGB pixels while retaining the alpha contour, outer shadow and central artwork. Inspect patterned corners individually and update the catalog source hash after an edit.

The build downsamples new source PNGs to 192 px. Original Sorcery PNGs are copied without changing their bytes. Image generation is an artwork authoring step; it is not a build dependency.
