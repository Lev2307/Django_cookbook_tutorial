import uuid
import contextlib
import os

from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill
from mptt.fields import TreeManyToManyField

from django.db import models
from django.urls import reverse
from django.utils.timezone import now as timezone_now
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from myproject.apps.core.models import UrlBase, CreationModificationDateBase
from myproject.apps.core.processors import WatermarkOverlay

from myproject.apps.core.model_fields import (
    MultilingualCharField,
    MultilingualTextField,
    TranslatedField
)





# FavoriteObjectBase = object_relation_base_factory(
#     is_required=True,
# )

# OwnerBase = object_relation_base_factory(
#     prefix="owner",
#     prefix_verbose=_("Owner"),
#     is_required=True,
#     add_related_name=True,
#     limit_content_type_choices_to={
#         "model__in": (
#         "user",
#         "group",
#         )
#     }
# )


# class Like(FavoriteObjectBase, OwnerBase):
#     class Meta:
#         verbose_name = _("Like")
#         verbose_name_plural = _("Likes")
    
#     def __str__(self):
#         return  _("{owner} likes {object}").format(
#                 owner=self.owner_content_object,
#                 object=self.content_object
#                  )

RATING_CHOICES = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

def upload_to(instance, filename):
    now = timezone_now()
    base, extension = os.path.splitext(filename)
    extension = extension.lower()
    return f"ideas/{now:%Y/%m}/{instance.pk}/{extension}"

class Idea(CreationModificationDateBase, UrlBase):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Author"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="authored_ideas",
    )
    
    categories_m2m = models.ManyToManyField(
        "categories.Category",
        verbose_name=_("Categories m2m"),
        related_name="category_ideas",
    )
    categories = TreeManyToManyField(
        "categories1.Category",
        verbose_name=_("Categories"),
    )

    rating = models.PositiveIntegerField(
        _("Rating"), choices=RATING_CHOICES, blank=True, null=True
    )
    title = models.CharField(
        _("Title"),
        max_length=200,
    )
    content = models.TextField(
        _("Content"),
        max_length=500
    )
    translated_title = TranslatedField("title")
    translated_content = TranslatedField("content")

    picture = models.ImageField(_("Image"), upload_to=upload_to)
    picture_social = ImageSpecField(
        source="picture",
        processors=[ResizeToFill(1024, 512)],
        format="JPEG",
        options={'quality': 100}
    )
    picture_large = ImageSpecField(
        source="picture",
        processors=[ResizeToFill(800, 400)],
        format="PNG"
    )
    picture_thumnail = ImageSpecField(
        source="picture",
        processors=[ResizeToFill(728, 250)],
        format="PNG"
    )

    watermarked_picture_large = ImageSpecField(
        source="picture",
        processors=[
            ResizeToFill(800, 400),
            WatermarkOverlay(
                watermark_image=os.path.join(settings.STATIC_ROOT, 'site', 'img', 'watermark.png'),
            )
        ],
        format="PNG"
    )

    class Meta:
        verbose_name = _("Idea")
        verbose_name_plural = _("Ideas")    
        constraints = [
            models.UniqueConstraint(
                fields=["title"],
                condition=models.Q(author=None),
                name="unique_titles_for_each_author",
            ),
            models.CheckConstraint(
                check=models.Q(
                    title__iregex=r"^\S.*\S$"
                    # starts with non-whitespace,
                    # ends with non-whitespace,
                    # anything in the middle
                ),
                name="title_has_no_leading_and_trailing_whitespaces",
            )
        ]

    def __str__(self):
        return self.title
    
    def get_url_path(self):
        return reverse("ideas:idea_detail", kwargs={"pk": self.pk})

    def clean(self):
        import re
        if self.author and Idea.objects.exclude(pk=self.pk).filter(author=self.author, title=self.title).exists():
            raise ValidationError(
                _("Each idea of the same user should have a unique title.")
            )
        if not re.match(r"^\S.*\S$", self.title):
            raise ValidationError(
                _("The title cannot start or end with a whitespace.")
            )

    def delete(self, *args, **kwargs):
        from django.core.files.storage import default_storage
        if self.picture:
            with contextlib.suppress(FileNotFoundError):
                default_storage.delete(
                    self.picture_social.path
                )
                default_storage.delete(
                    self.picture_large.path
                )
                default_storage.delete(
                    self.picture_thumbnail.path
                )
            self.picture.delete()
        super().delete(*args, **kwargs)

    @property
    def structured_data(self):
        from django.utils.translation import get_language
        lang_code = get_language()
        data = {
            "@type": "CreativeWork",
            "name": self.translated_title,
            "description": self.translated_content,
            "inLanguage": lang_code,
        }
        if self.author:
            data["author"] = {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username,
            }
        if self.picture:
            data["image"] = self.picture_social.url
        return data


class IdeaTranslations(models.Model):
    idea = models.ForeignKey(
        Idea,
        verbose_name=_("Idea"),
        on_delete=models.CASCADE,
        related_name="translations",
    )

    language = models.CharField(_("Language"), max_length=7)
    title = models.CharField(_("Title"), max_length=200)
    content = models.TextField( _("Content"))

    class Meta:
        verbose_name = _("Idea Translations")
        verbose_name_plural = _("Idea Translations")
        ordering = ["language"]
        unique_together = [["idea", "language"]]
        
    def __str__(self):
        return self.title
