# Launcher compatibility

The application exposes standard ADW/Nova/Apex icon pack discovery, resource XML and assets copies of appfilter/drawable metadata, and the ADW icon-picker activity. The pack applies dedicated art to mapped launcher components. Launchers control their own cache, fallback rendering and theme selection.

The dashboard provides offline browsing and search. Its **Apply** button explains where to select the pack; it does not change the current launcher or Global Icon Pack configuration automatically.

## Global Icon Pack

Global Icon Pack uses the first mapping for a package as its default icon. The pack gives Google Search the default for `com.google.android.googlequicksearchbox` and maps Gemini, Lens, Weather and Assistant by their exact activities. Dynamic calendars are listed first so Google Calendar also uses its daily icon for package-level lookups.

Select Sorcery_rebirth as the icon pack. For fallback icons, the pack provides a shadowed paper background (`iconback`), an inverse alpha mask (`iconmask`), a subtle paper sheen overlay (`iconupon`) and scale `0.70`. Launchers that support `<calendar>` entries also receive dynamic daily icons for mapped calendars such as Google Calendar (`com.google.android.calendar`). Square dedicated artwork has a paper face of approximately 79% of the canvas width. Global Icon Pack can override pack-supplied fallback options. The sizing of other silhouettes is covered in [Artwork direction](art-direction.md#source-and-launcher-sizes).

When using its custom shape override, the following 100 × 100 path aligns the fallback outline with the paper face of dedicated Sorcery icons:

```text
M16.4063,10.4167H83.5937A5.9896,5.9896,0,0,1,89.5833,16.4063V83.5937A5.9896,5.9896,0,0,1,83.5937,89.5833H16.4063A5.9896,5.9896,0,0,1,10.4167,83.5937V16.4063A5.9896,5.9896,0,0,1,16.4063,10.4167Z
```

The fallback face spans 79.1666% of the canvas, with an 11.5 px corner radius at the 192 px artwork scale (matching original Sorcery square tiles such as `aida64.png`). Use foreground scale `0.70`, non-adaptive scale `1.00`, foreground-only scaling enabled and the white shape background `#ffffffff`. Enable generated fallback icons, conversion to adaptive and fallback override. Keep “Fallback background as Adaptive background” disabled. These are user-controlled Global Icon Pack settings; the APK does not modify them.

Select the pack again or use the launcher's own icon refresh operation if cached images remain after changing themes. Keep existing desktop layouts and unrelated theme settings when refreshing icons.

When Global Icon Pack uses its icon database, it keeps existing mappings when an edited pack is updated. Restoring the affected package in Global Icon Pack reloads its mappings from the installed pack and replaces custom mappings for that package.

## Report a missing mapping

Include the app's display name, Android package ID, launcher activity, launcher name and app version. A package may have several launcher aliases, regional variants or work-profile installations. The catalog can hold multiple verified activity names for the same icon.
