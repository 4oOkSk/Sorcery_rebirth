# Artwork direction

New icons follow original Sorcery's vivid Material colors, clear white details, thin paper layers and directional shadows. The original pack supplies the style reference. Public application artwork supplies the mark: retain its silhouette, negative space, lettering, color relationships and arrangement.

The collection combines original Sorcery artwork with newly illustrated circular discs, hexagonal/shield badges, folded cards, notched tickets, layered objects and Material square faces with directional long shadows. Avoid placing a raw application icon inside an unstyled white or black square frame. Authoring method, public references and the source PNG hash are recorded per icon in `catalog/icons.json`.

## Style prompt

按照参考图中原版 Sorcery 图标包的设计语言、配色、质感、立体感、阴影和视觉大小，重新设计并绘制 Android 应用图标。

请先观察原版 Sorcery 作为一个整体的视觉特征，再把新应用自然地画进同一个图标家族。让新旧图标并排时，感觉来自同一位设计师、同一套作品。

配色遵循原版：鲜明、饱满、清爽的 Material 色彩，干净的白色和明确的明暗对比。参考支付宝和 Twitter 的明亮蓝、AIDA64 的红、Evernote 和 LINE 的绿。保留各应用的识别色，白色图形保持清亮。

造型与材质：严禁在原始图标外直接套一层白色或纯黑方框。根据应用特征采用双层圆形圆盘、正六边形折角徽章、右上折角卡片、打孔票券、盾牌、独立器物轮廓或满幅品牌色长投影方卡。准确保留核心品牌符号与字形，将表面材质、薄纸层、明暗、边缘和 45 度斜向长投影转为原版 Sorcery 风格。图标在手机桌面尺寸下应清晰、有份量、有细节。

各图标与全部阴影完整放在自己的格子内，四边保留透明空隙。协调方形、圆形和自由轮廓的视觉份量，统一正面视角与左上方光源，输出透明 PNG。

## Source and launcher sizes

Square paper faces and the fallback mask use a 23 px source corner radius (11.5 px at 192 px APK scale, matching original Sorcery tiles such as `aida64.png`). The common square face is 304/384, or 152/192. Global Icon Pack uses the matching path in [compatibility](compatibility.md). Circular discs, hexagonal badges, folded cards and illustrated objects are optically balanced to the same visual envelope (~304–324 px on a 384 px canvas).

`tools/extract_sheet.py` accepts a transparent 3×3 sheet and resource names in row-major order. It removes tiny isolated fragments, preserves disconnected parts of a mark and writes 384 px sources. Square faces use approximately 152/192 of the canvas; circular and freeform shapes use approximately 176/192. Shadows remain inside the transparent canvas. Review the results at launcher size on light and dark backgrounds.

Ordinary square paper faces occupy `(40, 40, 344, 344)` in a 384 px source: both dimensions become 152 px in the APK. Measure the straight face edges rather than the full shadow bounds. For a reviewed tile with an accidentally rectangular face, run `python3 tools/normalize_tiles.py rebirth_example` to inspect the correction, then repeat with `--write`. The tool adjusts both axes and placement with the existing artwork and shadow, checks the resulting face and canvas edges, and updates the catalog hash and `generation.square_face`. Review the result visually. Select ordinary square tiles individually; books, wallets, tickets, speech bubbles and other intentional silhouettes retain their own proportions.

To unify an ordinary tile's size and corner radius together, run `python3 tools/standardize_tiles.py rebirth_example --output .local/tasks/tile-review/output`. The tool first normalizes the face, then carries the existing rim shading to a 23 px radius with a smooth local deformation. RGB detail in the central 176 px square remains unchanged after size normalization. Contact and soft shadows follow the shared outline. Review the output beside the input, including lettering near the edges, before copying it into `artwork/icons/` and updating the catalog hash, `square_face` and `corner_radius`. Use explicitly reviewed square tiles; illustrated objects and separate paper layers keep their own contours.

Square tiles use one paper outline. Recover the original transparent face when an imported tile contains overlapping rounded edges or painted-over corners. Preserve its RGB edge shading, mark and internal shadows. `python3 tools/compose_tile.py material.png output.png` places a reviewed face in the standard 304 px square and generates contact and soft shadows from that face's own alpha contour. Larger native corners and disconnected paper layers retain their silhouettes. The input must contain the original face with its alpha, before any corner filling or outer-shadow composition; an opaque reference with a baked-in rounded background needs individual preparation. Use `--background R G B` only for a standalone mark that needs a paper backing.

Review corners and adjoining straight edges together at source, 192 px and launcher sizes, on light and dark backgrounds. Check both RGB shading and alpha: unchanged transparency alone does not establish that a shadow survived an edit. Confirm that lettering and internal shadows remain intact, that only one outer contour is visible, and that shadows fit inside the canvas. Update the catalog source hash and record the composition method after an edit.

The build downsamples new source PNGs to 192 px. Original Sorcery PNGs are copied without changing their bytes. Image generation is an artwork authoring step; it is not a build dependency.
