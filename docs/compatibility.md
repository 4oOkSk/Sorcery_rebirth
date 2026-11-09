# Launcher compatibility

The application exposes standard ADW/Nova/Apex icon pack discovery, resource XML and assets copies of appfilter/drawable metadata, and the ADW icon-picker activity. The pack applies dedicated art to mapped launcher components. Launchers control their own cache, fallback rendering and theme selection.

The dashboard provides offline browsing and search. Its **Apply** button explains where to select the pack; it does not change the current launcher or Global Icon Pack configuration automatically.

## Global Icon Pack

Select Sorcery_rebirth as the icon pack. For fallback icons, the pack provides a paper background, an inverse alpha mask and scale `0.70`. Square dedicated artwork has a paper face of approximately 79% of the canvas width; circular and freeform icons can extend to about 92%. Global Icon Pack can override pack-supplied fallback options.

When using its custom shape override, the following 100 × 100 path aligns the fallback outline with the paper face of dedicated Sorcery icons:

```text
M16.4512,10.1109H83.5488A6.3403,6.3403,0,0,1,89.8891,16.4512V83.5488A6.3403,6.3403,0,0,1,83.5488,89.8891H16.4512A6.3403,6.3403,0,0,1,10.1109,83.5488V16.4512A6.3403,6.3403,0,0,1,16.4512,10.1109Z
```

Use foreground scale `0.70`, non-adaptive scale `1.00`, foreground-only scaling enabled and the white shape background `#ffffffff`. Enable generated fallback icons, conversion to adaptive and fallback override. Keep “Fallback background as Adaptive background” disabled. These are user-controlled Global Icon Pack settings; the APK does not modify them.

Select the pack again or use the launcher's own icon refresh operation if cached images remain after changing themes. Keep existing desktop layouts and unrelated theme settings when refreshing icons.

## Report a missing mapping

Include the app's display name, Android package ID, launcher activity, launcher name and app version. A package may have several launcher aliases, regional variants or work-profile installations. The catalog can hold multiple verified activity names for the same icon.
