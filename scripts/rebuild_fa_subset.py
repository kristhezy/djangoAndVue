#!/usr/bin/env python3
"""
扫描所有 HTML 模板中的 fa-* 图标，从完整字体中提取 glyph 生成子集。
用法: python scripts/rebuild_fa_subset.py
"""
import os, re, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"
FONT_DIR    = PROJECT_ROOT / "static" / "font" / "webfonts"
CSS_FILE    = PROJECT_ROOT / "static" / "font" / "css" / "fa-subset.css"

STYLE_MAP = {
    "fa-solid":   ("fa-solid-900.woff2",),
    "fa-brands":  ("fa-brands-400.woff2",),
    "fa-regular": ("fa-regular-400.woff2",),
}
STYLE_SHORT = {"fas": "fa-solid", "fab": "fa-brands", "far": "fa-regular"}


# ── 1. 从 fa-subset.css 提取 icon_name → unicode 映射 ──────────
def load_icon_map():
    """解析 CSS，从每条规则中提取所有图标名→unicode映射"""
    css = CSS_FILE.read_text(encoding="utf-8")
    icon_map = {}

    # 每一条 CSS 规则格式: .fa-A:before,.fa-B:before,.fa-C:before{content:"\XXXX"}
    for m in re.finditer(
        r'((?:\.fa-[\w-]+:before,?\s*)+)\s*\{[^}]*?content\s*:\s*"\\([\da-fA-F]+)"',
        css
    ):
        selectors_block = m.group(1)  # e.g. ".fa-right-from-bracket:before,.fa-sign-out-alt:before"
        codepoint = m.group(2)
        for name_m in re.finditer(r'\.(fa-[\w-]+):before', selectors_block):
            icon_map[name_m.group(1)] = codepoint

    print(f"从 CSS 提取 {len(icon_map)} 个图标映射")
    return icon_map


# ── 2. 扫描模板 ─────────────────────────────────────────────
def scan_templates():
    used = set()
    # 扫描 HTML 模板
    for html_file in TEMPLATE_DIR.rglob("*.html"):
        _scan_file(html_file, used)
    # 也扫描 static/js/ 中的 JS 文件（图标可能在 JS 模板字符串里）
    js_dir = PROJECT_ROOT / "static" / "js"
    for js_file in js_dir.rglob("*.js"):
        _scan_file(js_file, used)
    print(f"扫描 {sum(1 for _ in TEMPLATE_DIR.rglob('*.html'))} 个模板 + {sum(1 for _ in js_dir.rglob('*.js'))} 个 JS 文件，{len(used)} 个图标")
    return used


def _scan_file(filepath, used):
    content = filepath.read_text(encoding="utf-8")
    for m in re.finditer(r'class="([^"]*)"', content):
        classes = m.group(1).split()
        style = icon = ""
        for c in classes:
            if c in ("fa-solid", "fa-brands", "fa-regular", "fas", "fab", "far"):
                style = STYLE_SHORT.get(c, c)
            elif c.startswith("fa-") and not c.startswith("fa-fw"):
                icon = c
        if icon:
            s = style or "fa-solid"
            used.add((s, icon))


# ── 3. 主流程 ───────────────────────────────────────────────
def main():
    icon_map = load_icon_map()
    used_icons = scan_templates()

    from fontTools.ttLib import TTFont # type: ignore
    from fontTools.subset import Subsetter # type: ignore

    for style_name, (font_file,) in STYLE_MAP.items():
        needed = [(s, i) for s, i in used_icons if s == style_name]
        if not needed:
            continue

        print(f"\n[{style_name}] {[i for _,i in needed]}")

        # icon_name → codepoint → glyph name
        full_path = FONT_DIR / font_file
        ft = TTFont(str(full_path))
        font_cmap = ft.getBestCmap()  # codepoint → glyph name

        glyph_names = set()
        for _, icon_name in needed:
            cp = icon_map.get(icon_name)
            if not cp:
                print(f"  ⚠ {icon_name}: CSS 中未找到")
                continue
            gn = font_cmap.get(int(cp, 16))
            if gn:
                glyph_names.add(gn)
            else:
                print(f"  ⚠ {icon_name} (U+{cp.upper()}): 完整字体中不存在")

        if not glyph_names:
            print(f"  无有效 glyph，跳过")
            continue

        subset_path = FONT_DIR / font_file.replace(".woff2", "-subset.woff2")

        sub = Subsetter()
        sub.populate(glyphs=glyph_names)
        sub.subset(ft)
        ft.flavor = 'woff2'

        if subset_path.exists():
            os.rename(str(subset_path), str(subset_path) + ".bak")
        ft.save(str(subset_path))
        size = os.path.getsize(str(subset_path))
        print(f"  ✅ {subset_path.name}: {size} bytes ({size/1024:.1f} KB)")

    print(f"\n完成！刷新页面即可。")
    print(f"加图标后: python scripts/rebuild_fa_subset.py")


if __name__ == "__main__":
    main()
