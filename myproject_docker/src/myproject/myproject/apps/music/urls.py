from django.urls import path
from .views import SongList

urlpatterns = [
    path("", SongList.as_view(), name="song_list"),
]
