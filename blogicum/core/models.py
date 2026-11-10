from django.db import models
from core.constants import MAX_TITLE_LENGTH


class PublishedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и поле created_at."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class TitleModel(models.Model):
    """Абстрактная модель. Добавляет поле title"""

    title = models.CharField(
        max_length=MAX_TITLE_LENGTH, verbose_name='Заголовок'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
