from django.shortcuts import render
from django.views.generic import ListView


from .models import Song

# Create your views here.

class SongList(ListView):
    queryset = Song.objects.all()