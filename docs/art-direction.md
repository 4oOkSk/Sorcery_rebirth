# Artwork direction

New icons follow original Sorcery's vivid Material colors, clear white details, thin paper layers and directional shadows. The original pack supplies the style reference. Public application artwork supplies the mark: retain its silhouette, negative space, lettering, color relationships and arrangement.

Verify each brand reference against the application's package and publisher in its official store listing or upstream project. Unrelated applications with the same display name need separate artwork and component mappings. Preserve distinctive dot arrangements, negative spaces and lettering when adding paper layers; review the result at 48 px on both light and dark backgrounds.

Design each illustration from the application's actual purpose and recognizable brand. Supply the generator with the package, a factual description of the app, its verified original icon and a varied board made from original Sorcery artwork. Let that context determine the concept and silhouette. An outer shape or paper fold needs a reason in the depicted object or action. Review new designs together: unrelated apps need individual constructions, and related apps need their distinguishing behavior and identity to remain visible. Authoring method, public references and the source PNG hash are recorded per icon in `catalog/icons.json`.

## Style prompt

按照参考图中原版 Sorcery 图标包的设计语言、配色、质感、立体感、阴影和视觉大小，重新设计并绘制 Android 应用图标。

请先观察原版 Sorcery 作为一个整体的视觉特征，再把新应用自然地画进同一个图标家族。让新旧图标并排时，感觉来自同一位设计师、同一套作品。

配色遵循原版：鲜明、饱满、清爽的 Material 色彩，干净的白色和明确的明暗对比。参考支付宝和 Twitter 的明亮蓝、AIDA64 的红、Evernote 和 LINE 的绿。保留各应用的识别色，白色图形保持清亮。

根据提供的应用用途、准确包名、真实品牌图标和原版 Sorcery 参考，自行构思这个应用独有的造型与结构。让功能与品牌共同参与设计；仅替换标志便能套给另一个应用的容器需要重新构思。外轮廓、薄纸层和折角应能解释为这个设计所需的具体物体或动作。避免重复使用盾牌、五边形、多边形、圆章和装饰性折角，也避免给同类应用统一换成另一种相同物件。品牌本身含盾牌或多边形时，准确保留必要标志，并让整体构图表达该应用的特征。

准确保留核心品牌符号、负形、点阵排列与字形，运用薄纸层、边缘明暗和 45 度斜向投影形成原版 Sorcery 的质感。保持清楚的平面关系和少量有意义的细节。逐张检查后，将新图标并排复查，淘汰重复构思、厚重亮面材质，以及在 48 px 深浅背景上无法读清的方案。

各图标与全部阴影完整放在自己的格子内，四边保留透明空隙。协调方形、圆形和自由轮廓的视觉份量，统一正面视角与左上方光源，输出透明 PNG。

## Source and launcher sizes

Square paper faces and the fallback mask use a 23 px source corner radius (11.5 px at 192 px APK scale, matching original Sorcery tiles such as `aida64.png`). The common square face is 304/384, or 152/192. Global Icon Pack uses the matching path in [compatibility](compatibility.md). Balance other silhouettes by visible area and weight beside the original icons; their longest solid dimension can extend to about 332 px on a 384 px canvas.

`tools/extract_sheet.py` accepts a transparent 3×3 sheet and resource names in row-major order. It groups connected components across the sheet before cropping and uses the same scale on both axes. On the 384 px output, the tool caps the longest opaque dimension at 304 px for well-filled, nearly square artwork and at 332 px for other shapes. Check that the crop preserves the artwork and shadows, then review the result at launcher size on light and dark backgrounds.

Ordinary square paper faces occupy approximately `(40, 40, 344, 344)` in a 384 px source. Measure straight face edges separately from shadow bounds. Scale generated artwork with one shared scale for both axes, retaining every nonzero alpha pixel and all shadows inside transparent margins. Preserve the generated silhouette and natural proportions. Redraw accidental geometry or inappropriate corner treatment; changing the width and height independently, deforming corners or cropping artwork to force a common size is not an accepted correction.

Square tiles use one paper outline. Recover the original transparent face when an imported tile contains overlapping rounded edges or painted-over corners. Preserve its RGB edge shading, mark and internal shadows. `python3 tools/compose_tile.py material.png output.png` places a reviewed face in the standard 304 px square and generates contact and soft shadows from that face's own alpha contour. Larger native corners and disconnected paper layers retain their silhouettes. The input must contain the original face with its alpha, before any corner filling or outer-shadow composition; an opaque reference with a baked-in rounded background needs individual preparation. Use `--background R G B` only for a standalone mark that needs a paper backing.

Review corners and adjoining straight edges together at source, 192 px and launcher sizes, on light and dark backgrounds. Check both RGB shading and alpha: unchanged transparency alone does not establish that a shadow survived an edit. Confirm that lettering and internal shadows remain intact, that only one outer contour is visible, and that shadows fit inside the canvas. Update the catalog source hash and record the composition method after an edit.

The build downsamples new source PNGs to 192 px. Original Sorcery PNGs are copied without changing their bytes. Image generation is an artwork authoring step; it is not a build dependency.
