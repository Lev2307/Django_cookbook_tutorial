from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.forms import modelformset_factory

from .models import Idea, IdeaTranslations, RATING_CHOICES
from .forms import IdeaForm, IdeaTranslationsForm, IdeaFilterForm


class IdeaList(ListView):
    model = Idea
    template_name = "ideas/idea_list.html"
    context_object_name = "ideas"

class IdeaDetail(DetailView):
    model = Idea
    context_object_name = "idea"
    template_name = "ideas/idea_detail.html"


@login_required
def add_or_change_idea(request, pk=None):
    idea = None
    if pk:
        idea = get_object_or_404(Idea, pk=pk)
    IdeaTranslationsFormSet = modelformset_factory(IdeaTranslations, form=IdeaTranslationsForm, extra=0, can_delete=True)
    if request.method == "POST":
        form = IdeaForm(
            request,
            data=request.POST,
            files=request.FILES,
            instance=idea
        )
        translations_formset = IdeaTranslationsFormSet(
            queryset=IdeaTranslations.objects.filter(idea=idea),
            data=request.POST,
            files=request.FILES,
            prefix="translations",
            form_kwargs={"request": request},
        )
        if form.is_valid() and translations_formset.is_valid():
            form = form.save()
            translations = translations_formset.save(commit=False)

            for translation in translations:
                translation.idea = idea
                translation.save()

            translations_formset.save_m2m()

            for translation in translations_formset.deleted_objects:
                translation.delete()

            return redirect("ideas:idea_list")
    else:
        form = IdeaForm(request, instance=idea)
        translations_formset = IdeaTranslationsFormSet(queryset=IdeaTranslations.objects.filter(idea=idea), prefix="translations", form_kwargs={'request': request})

    context = {"idea": idea, "form": form, "translations_formset": translations_formset}
    return render(request, 'ideas/idea_form.html', context)

@login_required
def delete_idea(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == "POST":
        idea.delete()
        return redirect("ideas:idea_list")
    context = {"idea": idea}
    return render(request, 'ideas/idea_deleting_confirmation.html', context)
    

def filter_facets(facets, qs, form, filters):
    for query_param, filter_param in filters:
        value = form.cleaned_data[query_param]
        print(value)
        if value:
            selected_value = value
            if query_param == "rating":
                rating = int(value)
                selected_value = (rating, dict(RATING_CHOICES)[rating])
            facets["selected"][query_param] = selected_value
            filter_args = {filter_param: value}
            qs = qs.filter(**filter_args).distinct()
    return qs


PAGE_SIZE = getattr(settings, "PAGE_SIZE", 24)

def idea_list(request):
    qs = Idea.objects.order_by("title")
    form = IdeaFilterForm(data=request.GET)

    facets = {
        "selected": {},
        "categories": {
            "authors": form.fields["author"].queryset,
            "categories": form.fields["category"].queryset,
            "ratings": RATING_CHOICES,
        },
    }
    print(facets)

    if form.is_valid():
        print(form.cleaned_data)
        filters = (
            # query parameter, filter parameter
            ("author", "author"),
            ("category", "categories"),
            ("rating", "rating"),
        )
        qs = filter_facets(facets, qs, form, filters)

    context = {"form": form, "facets": facets, "object_list": qs}
    return render(request, "ideas/idea_list.html", context)