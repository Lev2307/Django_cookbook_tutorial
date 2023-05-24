from django.views.generic import ListView

from .models import Article

class NewsList(ListView):
    model = Article