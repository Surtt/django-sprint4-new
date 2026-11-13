from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin

from .forms import CommentForm, PostForm, ProfileForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Comment, Post

POSTS_BY_PAGE = 10

User = get_user_model()


def get_visible_post(user, post_id):
    """Вернуть пост, если он доступен пользователю, иначе 404."""
    posts = Post.objects.with_related()
    post = get_object_or_404(posts, pk=post_id)
    if post.author != user:
        post = get_object_or_404(posts.published(), pk=post_id)
    return post


class PostListView(ListView):
    """Базовый список публикаций с постраничным выводом."""

    paginate_by = POSTS_BY_PAGE


class HomePage(PostListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.with_related().published().with_comment_count()


def post_detail(request, post_id):
    post = get_visible_post(request.user, post_id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


class CategoryPostsView(SingleObjectMixin, PostListView):
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Category.objects.filter(is_published=True)
        )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            self.object.posts.with_related().published().with_comment_count()
        )


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=(self.request.user.username,))


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', args=(self.object.id,))


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    """Удаление публикации с показом её данных на странице подтверждения."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile', args=(self.request.user.username,))


class ProfileDetailView(SingleObjectMixin, PostListView):
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        posts = self.object.posts.with_related()
        if self.request.user != self.object:
            posts = posts.published()
        return posts.with_comment_count()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=(self.request.user.username,))


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_visible_post(
            self.request.user, self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=(self.kwargs['post_id'],))


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
