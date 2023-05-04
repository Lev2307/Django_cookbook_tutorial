from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from myproject.apps.core.models import UrlBase, CreationModificationDateBase, MetaTagsBase, object_relation_base_factory

from myproject.apps.core.model_fields import (
    MultilingualCharField,
    MultilingualTextField,
    TranslatedField
)


FavoriteObjectBase = object_relation_base_factory(
    is_required=True,
)

OwnerBase = object_relation_base_factory(
    prefix="owner",
    prefix_verbose=_("Owner"),
    is_required=True,
    add_related_name=True,
    limit_content_type_choices_to={
        "model__in": (
        "user",
        "group",
        )
    }
)


class Like(FavoriteObjectBase, OwnerBase):
    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
    
    def __str__(self):
        return  _("{owner} likes {object}").format(
                owner=self.owner_content_object,
                object=self.content_object
            )

# class Idea(UrlBase, MetaTagsBase, CreationModificationDateBase):
#     title = MultilingualCharField(
#         _("Title"),
#         max_length=200
#     )
#     content = MultilingualTextField(
#         _("Content"),
#     )
#     # other fields…
#     class Meta:
#         verbose_name = _("Idea")
#         verbose_name_plural = _("Ideas")

#     def __str__(self):
#         return self.title

#     def get_url_path(self):
#         return reverse("idea_details", kwargs={
#             "idea_id": str(self.pk),
#         })
class Idea(models.Model):
    title = models.CharField(
        _("Title"),
        max_length=200,
    )
    content = models.TextField(
        _("Content"),
    )
    translated_title = TranslatedField("title")
    translated_content = TranslatedField("content")

    class Meta:
        verbose_name = _("Idea")
        verbose_name_plural = _("Ideas")

    def __str__(self):
        return self.title

class IdeaTranslations(models.Model):
    idea = models.ForeignKey(
        Idea,
        verbose_name=_("Idea"),
        on_delete=models.CASCADE,
        related_name="translations",
    )

    language = models.CharField(_("Language"), max_length=7)
    title = models.CharField(
        _("Title"),
        max_length=200,
    )
    content = models.TextField(
        _("Content"),
    )

    class Meta:
        verbose_name = _("Idea Translations")
        verbose_name_plural = _("Idea Translations")
        ordering = ["language"]
        unique_together = [["idea", "language"]]
        
    def __str__(self):
        return self.title