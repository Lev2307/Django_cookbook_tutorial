
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.contrib.auth.decorators import login_required


from .models import Location
from .forms import LocationForm


class LocationList(ListView):
    model = Location
    paginate_by = 3

class LocationDetail(DetailView):
    model = Location
    context_object_name = "location"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['key'] = settings.YANDEX_MAPS_API_KEY
        return c

@login_required
def add_or_change_location(request, pk=None):
    location = None
    if pk:
        location = get_object_or_404(Location, pk=pk)
    if request.method == "POST":
        form = LocationForm(request, data=request.POST, files=request.FILES, instance=location)
        if form.is_valid():
            location = form.save()
            return redirect("locations:location_detail", pk=location.pk)
    else:
        form = LocationForm(request, instance=location)

    context = {"location": location, "form": form}
    return render(request, "locations/location_form.html", context)