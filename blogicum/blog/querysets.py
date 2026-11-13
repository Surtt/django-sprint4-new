from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    """QuerySet для публикаций с готовыми цепочками фильтров."""

    def with_related(self):
        return self.select_related('category', 'author', 'location')

    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    def with_comment_count(self):
        return self.annotate(comment_count=models.Count('comments')).order_by(
            '-pub_date'
        )
