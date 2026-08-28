#!/Users/imc/djangoPlant/.venv/bin/python3
"""
FontAwesome 6 子集化脚本
=========================
- 自动从 text_config.py 和模板/JS 收集所有图标
- 从 all.min.css 提取 Unicode 码点
- 用 fontTools 裁剪字体文件（只保留使用的图标）
- 生成最小 CSS

用法：
    cd /Users/imc/djangoPlant
    python3 scripts/subset_fa.py

新增图标后只需重新跑一次即可。
"""

import re
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEXT_CONFIG = PROJECT_ROOT / "djangoPlant" / "config" / "text_config.py"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_JS_DIR = PROJECT_ROOT / "static" / "js"
ALL_CSS = PROJECT_ROOT / "static" / "font" / "css" / "all.min.css"
WEBFONTS_DIR = PROJECT_ROOT / "static" / "font" / "webfonts"

# 输出文件
OUTPUT_CSS = PROJECT_ROOT / "static" / "font" / "css" / "fa-subset.css"
OUTPUT_SUBSET_SUFFIX = "-subset"


def collect_icons_from_file(filepath, extra_icons=None):
    """
    从文件内容中搜索所有 <i class="...fa-xxx..."> 并提取图标名和风格。
    返回: {icon_name: set_of_styles}
    """
    if extra_icons is None:
        extra_icons = {}

    content = filepath.read_text()
    pattern = re.compile(r'<i\s+[^>]*class\s*=\s*["\']([^"\']*)["\']')

    for m in pattern.finditer(content):
        classes = m.group(1).split()
        style = None
        icon = None
        for c in classes:
            if c in ("fa-solid", "fa-brands", "fa-regular"):
                style = c
            elif c.startswith("fa-") and c not in (
                "fa-solid", "fa-brands", "fa-regular", "fa-classic",
                "fa-sharp", "fa-1x", "fa-2x", "fa-xs", "fa-sm", "fa-lg",
                "fa-xl", "fa-2xl", "fa-fw", "fa-ul", "fa-li", "fa-border",
                "fa-pull-left", "fa-pull-right",
            ) and not re.match(r'^fa-\d+x?$', c):
                icon = c
        if icon:
            if icon not in extra_icons:
                extra_icons[icon] = set()
            extra_icons[icon].add(style or "fa-solid")

    return extra_icons


def collect_all_icons():
    """收集项目中所有实际使用的图标。返回: {icon_name: [styles]}"""
    icon_styles = {}

    # 1. 从 text_config.py 的 ICONS 字典解析
    if TEXT_CONFIG.exists():
        icon_styles = collect_icons_from_file(TEXT_CONFIG, icon_styles)

    # 2. 扫描所有模板文件
    for tmpl in TEMPLATES_DIR.glob("*.html"):
        icon_styles = collect_icons_from_file(tmpl, icon_styles)

    # 3. 扫描 JS 文件中的动态 HTML
    for js_file in STATIC_JS_DIR.glob("*.js"):
        icon_styles = collect_icons_from_file(js_file, icon_styles)

    # 4. 扫描 djangoPlant/ 下的其他 .py 文件（视图可能生成 HTML）
    for py_file in PROJECT_ROOT.glob("djangoPlant/**/*.py"):
        if py_file.name == "text_config.py":
            continue
        try:
            icon_styles = collect_icons_from_file(py_file, icon_styles)
        except Exception:
            pass

    return {k: sorted(v) for k, v in icon_styles.items()}


def extract_codepoints(icon_set):
    """
    从 all.min.css 提取每个图标的 Unicode 码点。
    返回: {icon_name: codepoint (e.g. '\\f015')}
    """
    if not ALL_CSS.exists():
        raise FileNotFoundError(f"CSS 文件不存在: {ALL_CSS}")

    css = ALL_CSS.read_text()
    codepoints = {}

    for icon in sorted(icon_set):
        # 去掉 fa- 前缀（icon 变量本身已包含 fa-）
        icon_name = icon[3:] if icon.startswith('fa-') else icon
        escaped_name = re.escape(icon_name)
        # 匹配 .fa-ICONNAME:before{content:"\XXXX"}
        pat = re.compile(
            r'\.fa-' + escaped_name + r':before\{content:"(\\[0-9a-fA-F]{4,5})"\}'
        )
        m = pat.search(css)
        if m:
            codepoints[icon] = m.group(1)
        else:
            # 有些图标可能是多选器的一部分，用宽松匹配
            pat2 = re.compile(r'\.fa-' + escaped_name + r':before')
            if pat2.search(css):
                # 找到但格式不同，尝试提取
                idx = css.find(f'.fa-{icon_name}:before')
                chunk = css[idx:idx + 120]
                m3 = re.search(r'content:"(\\[0-9a-fA-F]{4,5})"', chunk)
                if m3:
                    codepoints[icon] = m3.group(1)
                else:
                    print(f"  ⚠ 未找到码点: {icon}")
            else:
                print(f"  ⚠ 图标不在 CSS 中: {icon}")

    return codepoints


def classify_icons(icon_styles, codepoints):
    """
    按字体文件分类图标，收集各字体需要的 Unicode 码点。
    返回: {'solid': [codepoints], 'brands': [...], 'regular': [...]}
    """
    fonts = {"solid": set(), "brands": set(), "regular": set()}

    for icon, styles in icon_styles.items():
        cp = codepoints.get(icon)
        if not cp:
            continue

        for style in styles:
            if style == "fa-brands":
                fonts["brands"].add(cp)
            elif style == "fa-regular":
                fonts["regular"].add(cp)
                # regular 图标同样存在于 solid 字体（权重不同）
                fonts["solid"].add(cp)
            else:  # fa-solid 或默认
                fonts["solid"].add(cp)

    return {k: sorted(v) for k, v in fonts.items()}


def subset_font(input_path, output_path, unicodes):
    """裁剪单个字体文件，只保留指定 Unicode 码点"""
    from fontTools.subset import Subsetter
    from fontTools.ttLib import TTFont

    if not input_path.exists():
        print(f"  ✘ 源字体不存在: {input_path}")
        return False

    font = TTFont(str(input_path))
    sub = Subsetter()
    # fontTools Subsetter 接受 Unicode 字符或 U+XXXX 格式
    sub.populate(unicodes=unicodes)
    sub.subset(font)

    font.save(str(output_path))
    font.close()
    return True


def codepoint_to_int(cp_str):
    """将 CSS 码点 '\f015' 转换为整数 Unicode 码点"""
    hex_val = cp_str.replace("\\", "")
    return int(hex_val, 16)


def generate_minimal_css(icon_set, codepoints):
    """生成 CSS：用子集字体 URL 替换全量字体 URL，其他不变"""

    css = ALL_CSS.read_text()

    # 简单替换：将 woff2 字体引用从原始文件改为子集文件
    minimal_css = css.replace(
        "url(../webfonts/fa-solid-900.woff2)",
        "url(../webfonts/fa-solid-900-subset.woff2)",
    )
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-brands-400.woff2)",
        "url(../webfonts/fa-brands-400-subset.woff2)",
    )
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-regular-400.woff2)",
        "url(../webfonts/fa-regular-400-subset.woff2)",
    )
    # 替换 v4compatibility 的引用（保留规则但指向空，或也指向 solid subset）
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-v4compatibility.woff2)",
        "url(../webfonts/fa-solid-900-subset.woff2)",
    )
    # 同样替换 ttf 回退URL
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-solid-900.ttf)",
        "url(../webfonts/fa-solid-900-subset.woff2)",
    )
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-brands-400.ttf)",
        "url(../webfonts/fa-brands-400-subset.woff2)",
    )
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-regular-400.ttf)",
        "url(../webfonts/fa-regular-400-subset.woff2)",
    )
    minimal_css = minimal_css.replace(
        "url(../webfonts/fa-v4compatibility.ttf)",
        "url(../webfonts/fa-solid-900-subset.woff2)",
    )

    return minimal_css


def main():
    print("=" * 60)
    print("FontAwesome 6 子集化脚本")
    print("=" * 60)

    # Step 1: 收集图标
    print("\n[1/4] 扫描项目中的图标使用...")
    icon_styles = collect_all_icons()
    print(f"  发现 {len(icon_styles)} 个唯一图标：")
    for icon, styles in sorted(icon_styles.items()):
        print(f"    {icon:<30} → {', '.join(styles)}")

    if not icon_styles:
        print("  ✘ 未发现任何图标，退出")
        sys.exit(1)

    # Step 2: 提取码点
    print("\n[2/4] 从 all.min.css 提取 Unicode 码点...")
    codepoints = extract_codepoints(icon_styles)
    found = sum(1 for v in codepoints.values() if v)
    print(f"  成功: {found}/{len(icon_styles)}")

    if found == 0:
        print("  ✘ 未提取到任何码点，退出")
        sys.exit(1)

    # Step 3: 分类 & 裁剪字体
    print("\n[3/4] 裁剪字体文件...")
    font_unicodes = classify_icons(icon_styles, codepoints)

    font_map = {
        "solid": (
            WEBFONTS_DIR / "fa-solid-900.woff2",
            WEBFONTS_DIR / f"fa-solid-900{OUTPUT_SUBSET_SUFFIX}.woff2",
        ),
        "brands": (
            WEBFONTS_DIR / "fa-brands-400.woff2",
            WEBFONTS_DIR / f"fa-brands-400{OUTPUT_SUBSET_SUFFIX}.woff2",
        ),
        "regular": (
            WEBFONTS_DIR / "fa-regular-400.woff2",
            WEBFONTS_DIR / f"fa-regular-400{OUTPUT_SUBSET_SUFFIX}.woff2",
        ),
    }

    for font_type, (src, dst) in font_map.items():
        unicodes_hex = font_unicodes.get(font_type, [])
        if not unicodes_hex:
            print(f"  ⊘ {font_type}: 无图标，跳过")
            continue

        # 转为 Unicode 码点整数
        unicode_ints = [codepoint_to_int(cp) for cp in unicodes_hex]
        codepoints_str = ", ".join(
            f"U+{cp.replace(chr(92), '')}" for cp in unicodes_hex
        )

        print(f"  ... 裁剪 {src.name} ({len(unicode_ints)} 个码点: {codepoints_str})")
        ok = subset_font(src, dst, unicode_ints)
        if ok:
            orig_size = src.stat().st_size
            new_size = dst.stat().st_size
            reduction = (1 - new_size / orig_size) * 100
            print(f"    ✓ {dst.name}: {orig_size//1024}KB → {new_size//1024}KB (减少 {reduction:.0f}%)")

    # Step 4: 生成最小 CSS
    print("\n[4/4] 生成最小 CSS...")
    minimal_css = generate_minimal_css(icon_styles, codepoints)
    OUTPUT_CSS.write_text(minimal_css, encoding="utf-8")
    print(f"  ✓ {OUTPUT_CSS}")
    print(f"    原 CSS: {ALL_CSS.stat().st_size//1024}KB → 子集 CSS: {OUTPUT_CSS.stat().st_size//1024}KB")

    # 总结
    print("\n" + "=" * 60)
    print("✅ 子集化完成！")
    print(f"   图标数量: {len(icon_styles)}")
    print(f"   CSS 文件: {OUTPUT_CSS}")
    print(f"   字体文件: {WEBFONTS_DIR}/fa-*-subset.woff2")

    # 提示下一步
    print(f"\n💡 下一步: 在 base.html 中将引用从 all.min.css 改为 fa-subset.css")
    print("=" * 60)


if __name__ == "__main__":
    main()
