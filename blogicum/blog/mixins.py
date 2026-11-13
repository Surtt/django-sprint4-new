from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Comment, Post


class OnlyAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Пускает к объекту только его автора, остальных ведёт на пост."""

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id', self.kwargs.get('pk'))
        return redirect(reverse('blog:post_detail', args=(post_id,)))


class CommentMixin:
    """Общие настройки для редактирования и удаления комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    post_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs[self.pk_url_kwarg],
            post_id=self.kwargs[self.post_url_kwarg],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs[self.post_url_kwarg]]
        )


class PostMixin:
    """Общие настройки для создания, редактирования и удаления публикации."""

    model = Post
    template_name = 'blog/create.html'
