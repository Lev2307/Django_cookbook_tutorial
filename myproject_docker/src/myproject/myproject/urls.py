"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib.sitemaps import GenericSitemap

from myproject.apps.core import views as core_views

from myproject.apps.categories1 import views as categories_views

from myproject.apps.external_auth import views as external_auth_views
from myproject.apps.music.models import Song
from myproject.apps.music.views import RESTSongList, RESTSongDetail



class MySitemap(GenericSitemap):
    limit = 50

    def location(self, obj):
        return obj.get_url_path()

song_info_dict = {
    "queryset": Song.objects.all(),
    "date_field": "modified",
}

sitemaps = {"music": MySitemap(song_info_dict, priority=1.0)}

urlpatterns = [
    path("sitemap.xml", sitemaps_views.index, {"sitemaps": sitemaps}),
    path("sitemap-<str:section>.xml", sitemaps_views.sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

urlpatterns += i18n_patterns(
    path("", external_auth_views.index, name="index"),
    path("dashboard/", external_auth_views.dashboard, name="dashboard"),
    path("logout/", external_auth_views.logout, name="auth0_logout"),
    path("", include("social_django.urls")),
    # path("", lambda request: redirect("locations:location_list")),
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path("management/", admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path("ideas/", include(("myproject.apps.ideas.urls", "ideas"), namespace="ideas")),
    path("idea-categories/", categories_views.IdeaCategoryList.as_view(), name="idea_categories"),
    path("locations/", include(("myproject.apps.locations.urls", "locations"), namespace="locations")),
    path("news/", include(("myproject.apps.news.urls", "news"), namespace="news")),
    path("likes/", include(("myproject.apps.likes.urls", "likes"), namespace="likes")),
    path("search/", include("haystack.urls")),
    path("songs/", include(("myproject.apps.music.urls", "music"), namespace="music")),
    path("videos/", include("myproject.apps.viral_videos.urls")),
    path("js-settings/", core_views.js_settings, name="js_settings"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("rest-api/songs/", RESTSongList.as_view(), name="rest_song_list"),
    path("rest-api/songs/<uuid:pk>/", RESTSongDetail.as_view(), name="rest_song_detail"),
)

urlpatterns += [
    path(
        "upload-file/",
        core_views.upload_file,
        name="upload_file",
    ),
    path(
        "delete-file/",
        core_views.delete_file,
        name="delete_file",
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)