from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.vary import vary_on_cookie

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from yatube.settings import CACHE_TTL, DELTA_PAGE_COUNT, MAX_PAGE_COUNT


def my_paginator(
        page_list,
        page_number,
        dcount=DELTA_PAGE_COUNT,
        count=MAX_PAGE_COUNT,
):
    """Return dictionary of variables for the paginator.

    It is necessary to display the first, last page, the current one and
    'dcount' pages before and after current one.
    'count' is a maximum posts per page.
    """
    paginator = Paginator(page_list, count)
    page = paginator.get_page(page_number)
    from_page = max(page.number - dcount, 2)
    to_page = min(page.number + dcount, paginator.num_pages - 1)
    return {
        'from_page': from_page,
        'to_page': to_page,
        'page': page,
    }


@cache_page(CACHE_TTL, key_prefix='index_page')
@vary_on_cookie
def index(request):
    """Return page with MAX_PAGE_COUNT posts."""
    post_list = Post.objects.select_related(
        'author',
        'group',
    ).prefetch_related(
        'comments',
    )
    context = my_paginator(
        post_list,
        request.GET.get('page'),
    )
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Return the MAX_PAGE_COUNT posts in the selected group."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').prefetch_related(
        'comments')
    paginator = my_paginator(post_list, request.GET.get('page'))
    context = {
        **paginator,
        'group': group,
    }
    return render(request, 'posts/group.html', context)


def profile(request, username):
    """Shows user profile"""
    user = get_object_or_404(User, username=username)
    post_list = user.posts.select_related('group').prefetch_related('comments')
    paginator = my_paginator(post_list, request.GET.get('page'))
    following = request.user.is_authenticated and request.user.follower.filter(
        author=user).exists()
    context = {
        **paginator,
        'author': user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    """Shows the selected post."""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    context = {'form': form, 'post': post}
    return render(request, 'posts/post.html', context)


@login_required
@require_POST
def add_comment(request, username, post_id):
    """Add new post's comment in blog."""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(
        request.POST,
        instance=Comment(author=request.user, post=post)
    )
    if form.is_valid():
        form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
@require_http_methods(('GET', 'POST'))
def new_post(request):
    """Add new record in blog.

    This method form a page for writeing new post and check it one.
    If all fields are correct, the new record will be added to the
    database and the user will be redirected to the selected group.
    If some fields are incorrect, the user will receive information
    about it and can try to enter them again.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=Post(author=request.user)
    )
    if form.is_valid():
        form.save()
        return redirect('index')
    context = {'form': form}
    return render(request, 'posts/manage_post.html', context)


@require_http_methods(('GET', 'POST'))
@login_required
def post_edit(request, username, post_id):
    """Edit record in blog.

    This method form a page for edit post and check it one.
    If all fields are correct, the record will be updated in the
    database and the user will be redirected to post page.
    If some fields are incorrect, the user will receive information
    about it and can try to enter them again.
    """
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    context = {'post': post, 'form': form}
    return render(request, 'posts/manage_post.html', context)


@login_required
@require_POST
def post_delete(request, username, post_id):
    """Delete the author's post."""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    post.delete()
    return redirect(request.POST['this_url'])


def page_not_found(request, exception=None):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


@login_required
def follow_index(request):
    """Return a page with posts by subscribed authors."""
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group').prefetch_related('comments')
    context = my_paginator(
        post_list,
        request.GET.get('page'),
    )
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Subscribe the user on the author."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe the user from the author."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('profile', username=username)
