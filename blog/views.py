from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Category, Post, Comment
from django.core.paginator import Paginator
from django.contrib.auth import logout

def logout_view(request):
    """Функція для виходу з акаунту з прямим перенаправленням на головну"""
    logout(request)
    return redirect('post_list')

def category_list(request):
    """Відображення списку категорій з кількістю статей"""
    categories = Category.objects.annotate(posts_count=Count('posts')).order_by('name')

    context = {
        'categories': categories,
    }
    return render(request, 'blog/category_list.html', context)


def category_posts(request, slug):
    """Відображення статей певної категорії"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, published=True).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'posts': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)


def post_list(request):
    """Відображення списку статей з сортуванням"""
    sort_by = request.GET.get('sort', 'date')

    if sort_by == 'comments':
        posts = Post.objects.filter(published=True).annotate(
            comments_count=Count('comments')
        ).order_by('-comments_count')
    else:
        posts = Post.objects.filter(published=True).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'sort_by': sort_by,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Відображення деталей статті з коментарями"""
    post = get_object_or_404(Post, slug=slug, published=True)
    comments = post.comments.all()

    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('post_detail', slug=slug)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def delete_comment(request, comment_id):
    """Видалення коментаря"""
    comment = get_object_or_404(Comment, id=comment_id)

    # Перевірка прав доступу: автор коментаря або адміністратор
    if request.user == comment.author or request.user.is_staff:
        comment.delete()

    return redirect('post_detail', slug=comment.post.slug)


@login_required
def edit_post(request, slug):
    """Редагування статті"""
    post = get_object_or_404(Post, slug=slug)

    # Перевірка прав доступу: автор статті або адміністратор
    if request.user != post.author and not request.user.is_staff:
        return redirect('post_detail', slug=slug)

    if request.method == 'POST':
        # Обробка форми редагування
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.save()
        return redirect('post_detail', slug=post.slug)

    context = {
        'post': post,
    }
    return render(request, 'blog/edit_post.html', context)


@login_required
def delete_post(request, slug):
    """Видалення статті"""
    post = get_object_or_404(Post, slug=slug)

    # Перевірка прав доступу: автор статті або адміністратор
    if request.user == post.author or request.user.is_staff:
        post.delete()
        return redirect('post_list')

    return redirect('post_detail', slug=slug)