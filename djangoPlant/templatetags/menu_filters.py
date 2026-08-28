"""菜单权限 template filters。

sidebar.html 里 `{% load menu_filters %}` 后用：
- `{% if menus|has_menu:'soon' %}`            单个菜单 key 判断
- `{% if menus|has_any_menu:'a,b,c' %}`       分组容器：任一子项有权限即显示
"""
from django import template

register = template.Library()


@register.filter(name='has_menu')
def has_menu(menus, menu_key):
    """判断 menu_key 是否在 menus 集合中"""
    if not menus:
        return False
    return menu_key in menus


@register.filter(name='has_any_menu')
def has_any_menu(menus, keys):
    """判断 keys（逗号分隔）中是否至少有一个在 menus 中"""
    if not menus:
        return False
    for k in str(keys).split(','):
        if k.strip() in menus:
            return True
    return False
