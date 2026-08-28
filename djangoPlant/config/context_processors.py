from .text_config import SITE_CONFIG


def site_config(request):
    return {
        'config': SITE_CONFIG,
        'is_plain': request.GET.get('_plain') == '1',
        'menus': request.session.get('menus', []),
    }
