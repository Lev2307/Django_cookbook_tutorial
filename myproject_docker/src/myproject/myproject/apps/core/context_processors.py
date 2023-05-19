from django.conf import settings

def website_url(request):
    return {
        'WEBSITE_URL': settings.WEBSITE_URL
    }

def yandex_maps(request):
    return {
        'YANDEX_MAPS_API_KEY': settings.YANDEX_MAPS_API_KEY
    }