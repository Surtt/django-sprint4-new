from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

POSTS_BY_PAGE = 10

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

        def handle_no_permission(self):
            if not self.request.user.is_authenticated:
                return super().handle_no_permission()
            post_id = self.kwargs.get('post_id', self.kwargs.get('pk'))
            return redirect(reverse('blog:post_detail', args=[post_id]))


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['post_id'],
        )

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class HomePage(ListView):
    template_name = 'blog/index.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        return Post.objects.with_related().published().with_comment_count()


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.with_related(),
        pk=post_id,
    )

    if post.author != request.user:
        post = get_object_or_404(
            Post.objects.with_related().published(),
            pk=post_id,
        )
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all().select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return (
            self.category.posts.with_related().published().with_comment_count()
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.id])


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class ProfileDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        posts = Post.objects.filter(author=self.author)

        if self.request.user != self.author:
            posts = posts.published()

        posts = posts.with_comment_count()
        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.post_obj.pk])


class CommentUpdateView(
    LoginRequiredMixin, CommentMixin, OnlyAuthorMixin, UpdateView
):
    form_class = CommentForm


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, OnlyAuthorMixin, DeleteView
):
    pass
