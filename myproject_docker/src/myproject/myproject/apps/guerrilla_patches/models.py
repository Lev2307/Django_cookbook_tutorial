from django.db import models
from django.utils import text

from transliterate import slugify

# Create your models here.

text.slugify = slugify