from django.views.generic import ListView, DetailView
from django.conf import settings


from .models import Location


class LocationList(ListView):
    model = Location
    paginate_by = 10

class LocationDetail(DetailView):
    model = Location
    context_object_name = "location"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['key'] = settings.YANDEX_MAPS_API_KEY
        return c
