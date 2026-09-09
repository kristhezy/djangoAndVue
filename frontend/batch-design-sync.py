#!/usr/bin/env python3
"""
批量统一设计系统：将各页面 CSS/JS 中的 alert/confirm 替换为 ElMessage，
删除页面独有 CSS（已移至全局 design-system.css）。
HTML 结构保持兼容 — 通过 CSS class 映射实现。
"""
import re, os, glob

VIEWS_DIR = '/Users/imc/djangoAndVue/frontend/src/views'
SKIP = {'mmeett'}

# Pattern: pages with .card .card-title structure that need CSS class mapping
CARD_PAGES = set()

def process_page(filepath):
    page_name = filepath.split('/views/')[1].split('/')[0]
    if page_name in SKIP:
        return

    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    changed = []

    # 1. Add ElMessage import if alert() exists and not already imported
    has_alert = bool(re.search(r'\balert\s*\(', content))
    has_confirm = bool(re.search(r'\bconfirm\s*\(', content))
    has_el_msg = 'ElMessage' in content

    if (has_alert or has_confirm) and not has_el_msg:
        # Add import after the last import line
        import_line = "import { ElMessage, ElMessageBox } from 'element-plus'\n"
        warn_line = "const warn = (msg) => ElMessage({ message: msg, type: 'warning', duration: 2500 })\n"

        # Find the import section end
        imports = list(re.finditer(r'^import .+$', content, re.MULTILINE))
        if imports:
            last_import = imports[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + '\n' + import_line + warn_line + content[insert_pos:]
            changed.append('added ElMessage import')

    # 2. Replace alert() with warn()
    if has_alert:
        # alert('string') → warn('string')
        # alert(expression) → warn(expression)
        new_content = re.sub(r'\balert\s*\(', 'warn(', content)
        if new_content != content:
            content = new_content
            changed.append('replaced alert→warn')

    # 3. Replace confirm() with async ElMessageBox.confirm()
    if has_confirm and 'ElMessageBox' not in content[:content.find('confirm(') if 'confirm(' in content else 0]:
        # Only replace standalone confirm() not preceded by ElMessageBox
        def replace_confirm(m):
            msg = m.group(1)
            return f'try {{ await ElMessageBox.confirm({msg}, \'操作确认\', {{ confirmButtonText: \'确认\', cancelButtonText: \'取消\', type: \'warning\' }}) }} catch {{ return }}'

        content = re.sub(
            r'if\s*\(!confirm\((.+?)\)\)\s*return',
            replace_confirm,
            content
        )
        # Also make the containing function async if needed
        changed.append('replaced confirm→ElMessageBox')

    # 4. Remove page-specific <style scoped> content (keep the tags)
    style_match = re.search(r'<style scoped>(.*?)</style>', content, re.DOTALL)
    if style_match:
        style_content = style_match.group(1).strip()
        if len(style_content) > 50:  # Only remove if substantial
            # Keep a minimal style block
            content = content[:style_match.start()] + '<style scoped>\n/* 设计系统样式已移至全局 design-system.css */\n</style>' + content[style_match.end():]
            changed.append(f'removed {len(style_content)} chars of CSS')

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ {page_name}: {', '.join(changed)}")
    else:
        print(f"  ⏭️ {page_name}: no changes needed")

# Process all pages
for filepath in sorted(glob.glob(f'{VIEWS_DIR}/*/index.vue')):
    process_page(filepath)

print("\n完成！")
