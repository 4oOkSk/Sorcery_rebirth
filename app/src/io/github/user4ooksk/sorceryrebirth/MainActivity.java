/* Copyright 2026 4oOkSk. SPDX-License-Identifier: GPL-2.0-only */
package io.github.user4ooksk.sorceryrebirth;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Locale;

/** Offline icon catalog and launcher icon picker, using Android platform APIs. */
public final class MainActivity extends Activity {
    private final ArrayList<Entry> all = new ArrayList<>();
    private final ArrayList<Entry> shown = new ArrayList<>();
    private final IconAdapter adapter = new IconAdapter();
    private String collection = "Rebirth";
    private String query = "";
    private TextView count;
    private boolean picking;

    private static final class Entry {
        final String id, label, region, searchable;
        Entry(String[] fields) {
            id = fields[0]; label = fields[1]; region = fields[2];
            searchable = String.join(" ", fields).toLowerCase(Locale.ROOT);
        }
    }

    private int dp(float value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        picking = "org.adw.launcher.icons.ACTION_PICK_ICON".equals(getIntent().getAction());
        getWindow().setStatusBarColor(Color.rgb(244, 240, 232));
        getWindow().setNavigationBarColor(Color.rgb(244, 240, 232));
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(getAssets().open("catalog.tsv"), "UTF-8"))) {
            String line;
            while ((line = reader.readLine()) != null) all.add(new Entry(line.split("\t", -1)));
        } catch (Exception error) {
            throw new IllegalStateException("Cannot load icon catalog", error);
        }
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setBackgroundColor(Color.rgb(244, 240, 232));
        page.setPadding(dp(16), dp(16), dp(16), 0);
        page.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(dp(16) + insets.getSystemWindowInsetLeft(), dp(16) + insets.getSystemWindowInsetTop(), dp(16) + insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        TextView title = new TextView(this);
        title.setText("Sorcery_rebirth"); title.setTextSize(29); title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setTextColor(Color.rgb(38, 53, 47));
        page.addView(title);
        TextView subtitle = new TextView(this);
        subtitle.setText(picking ? "Choose an icon" : "Vivid colors. Paper layers. Familiar marks.");
        subtitle.setTextSize(13); subtitle.setPadding(0, dp(8), 0, dp(12)); page.addView(subtitle);
        LinearLayout buttons = new LinearLayout(this);
        for (String label : new String[]{"Rebirth", "CN", "JP", "Original"}) {
            Button button = new Button(this); button.setText(label); button.setTextSize(12); button.setAllCaps(false);
            button.setOnClickListener(view -> { collection = label; filter(); });
            buttons.addView(button, new LinearLayout.LayoutParams(0, dp(44), 1));
        }
        page.addView(buttons);
        EditText search = new EditText(this);
        search.setSingleLine(true); search.setHint("Search · 搜索 · 検索"); search.setTextSize(15);
        search.setInputType(android.text.InputType.TYPE_CLASS_TEXT);
        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int c, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int c) { query = s.toString().toLowerCase(Locale.ROOT).trim(); filter(); }
            public void afterTextChanged(Editable text) {}
        });
        page.addView(search, new LinearLayout.LayoutParams(-1, dp(52)));
        count = new TextView(this); count.setTextSize(12); count.setPadding(dp(4), dp(8), 0, dp(8)); page.addView(count);
        GridView grid = new GridView(this);
        grid.setNumColumns(GridView.AUTO_FIT); grid.setColumnWidth(dp(100)); grid.setStretchMode(GridView.STRETCH_COLUMN_WIDTH);
        grid.setVerticalSpacing(dp(4)); grid.setAdapter(adapter);
        grid.setOnItemClickListener((parent, view, position, id) -> select(shown.get(position)));
        page.addView(grid, new LinearLayout.LayoutParams(-1, 0, 1));
        if (!picking) {
            LinearLayout footer = new LinearLayout(this);
            Button apply = new Button(this); apply.setText("Apply / 应用"); apply.setAllCaps(false);
            apply.setOnClickListener(view -> new AlertDialog.Builder(this).setTitle("Apply icon pack").setMessage("Choose Sorcery_rebirth in your launcher's icon pack settings, or select it in Global Icon Pack.\n\n在桌面或 Global Icon Pack 的图标包设置中选择 Sorcery_rebirth。\n\nランチャーのアイコンパック設定で Sorcery_rebirth を選んでください。").setPositiveButton("OK", null).show());
            footer.addView(apply, new LinearLayout.LayoutParams(0, dp(48), 1));
            Button about = new Button(this); about.setText("About / 源码"); about.setAllCaps(false);
            about.setOnClickListener(view -> new AlertDialog.Builder(this).setTitle("Sorcery_rebirth 1.0.1").setMessage("Copyright 2026 4oOkSk\nOriginal Sorcery artwork © sorcererxw and contributors.\nCode and original Sorcery artwork: GPL-2.0, without warranty. Individual artwork sources and licenses are recorded in the catalog.\n\nRebirth artwork combines GPT illustrations and adaptations of public application marks. Style: original Sorcery. Symbol references: Simple Icons (CC0 subset), public app stores and upstream projects. Brand marks belong to their respective owners. The F-Droid artwork retains CC-BY-SA-3.0.\n\nSource artwork and license notices accompany every release.").setPositiveButton("Source & licenses", (dialog, which) -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/4oOkSk/Sorcery_rebirth")))).setNegativeButton("Close", null).show());
            footer.addView(about, new LinearLayout.LayoutParams(0, dp(48), 1)); page.addView(footer);
        }
        setContentView(page); filter();
    }

    private void filter() {
        shown.clear();
        for (Entry entry : all) {
            boolean region = collection.equals("Rebirth") ? !entry.region.equals("Original") : entry.region.equals(collection);
            if (region && (query.isEmpty() || entry.searchable.contains(query))) shown.add(entry);
        }
        if (count != null) count.setText(shown.size() + " icons · " + collection);
        adapter.notifyDataSetChanged();
    }

    private void select(Entry entry) {
        int resource = getResources().getIdentifier(entry.id, "drawable", getPackageName());
        if (picking) {
            Intent result = new Intent();
            result.putExtra(Intent.EXTRA_SHORTCUT_ICON_RESOURCE, Intent.ShortcutIconResource.fromContext(this, resource));
            Drawable drawable = getDrawable(resource);
            Bitmap bitmap = Bitmap.createBitmap(192, 192, Bitmap.Config.ARGB_8888);
            drawable.setBounds(0, 0, 192, 192); drawable.draw(new Canvas(bitmap));
            result.putExtra(Intent.EXTRA_SHORTCUT_ICON, bitmap); setResult(RESULT_OK, result); finish();
        } else {
            ImageView image = new ImageView(this); image.setImageResource(resource); image.setPadding(dp(48), dp(24), dp(48), dp(24));
            image.setAdjustViewBounds(true);
            new AlertDialog.Builder(this).setTitle(entry.label).setView(image).setPositiveButton("OK", null).show();
        }
    }

    private final class IconAdapter extends BaseAdapter {
        public int getCount() { return shown.size(); }
        public Entry getItem(int position) { return shown.get(position); }
        public long getItemId(int position) { return position; }
        public View getView(int position, View recycled, ViewGroup parent) {
            LinearLayout tile;
            if (recycled == null) {
                tile = new LinearLayout(MainActivity.this); tile.setOrientation(LinearLayout.VERTICAL); tile.setGravity(Gravity.CENTER_HORIZONTAL);
                tile.setPadding(dp(3), dp(4), dp(3), dp(8));
                ImageView image = new ImageView(MainActivity.this); image.setScaleType(ImageView.ScaleType.FIT_CENTER);
                tile.addView(image, new LinearLayout.LayoutParams(dp(84), dp(84)));
                TextView label = new TextView(MainActivity.this); label.setTextSize(11); label.setGravity(Gravity.CENTER); label.setMaxLines(2);
                label.setTextColor(Color.rgb(38, 53, 47)); tile.addView(label, new LinearLayout.LayoutParams(-1, dp(34)));
            } else tile = (LinearLayout) recycled;
            Entry entry = shown.get(position);
            int resource = getResources().getIdentifier(entry.id, "drawable", getPackageName());
            ((ImageView) tile.getChildAt(0)).setImageResource(resource);
            ((TextView) tile.getChildAt(1)).setText(entry.label);
            tile.setContentDescription(entry.label + " · " + entry.id);
            return tile;
        }
    }
}
