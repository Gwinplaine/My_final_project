from logging import NullHandler
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Blogtopic, Blogentry, Blogcomment
from .forms import BlogentryForm, BlogcommentForm


# функция представления всех разделов на странице
def blog(request):
    blogtop = Blogentry.objects.order_by('-blogdate_added')
    read_more = '...продолжить читать статью'
    for blogentry in blogtop:
        blogtopic = blogentry.blogtopic
        blockid = blogtopic.id
        if len(blogentry.blogtext) > 50:
            blogentry.blogtext = f"{blogentry.blogtext[:50]}"
        if len(blogentry.blogtitle) > 50:
            blogentry.blogtitle = f"{blogentry.blogtitle[:50]}..."
    context = {'blogtop': blogtop, 'read_more': read_more, 'blogtopic': blogtopic, 'id': blockid}
    return render(request, 'blog/blogindex.html', context)


@login_required
def blogtopics(request):
    blogtopics = Blogtopic.objects.order_by('blogdate_added')
    context = {'blogtopics': blogtopics}
    return render(request, 'blog/blogtopics.html', context)


# функция представления всех статей раздела на странице
@login_required
def blogtopic(request, blogtopic_id):
    blogtopic = Blogtopic.objects.get(id=blogtopic_id)
    read_more = '...продолжить читать статью'
    blogentries = blogtopic.blogentry_set.order_by('-blogdate_added')
    for blogentry in blogentries:
        if len(blogentry.blogtext) > 50:
            blogentry.blogtext = blogentry.blogtext[:50]
    context = {'blogtopic': blogtopic, 'blogentries': blogentries, 'read_more': read_more}
    return render(request, 'blog/blogtopic.html', context)


# функция добавления новой статьи в раздел
@login_required
def new_blogentry(request, blogtopic_id):
    blogtopic = Blogtopic.objects.get(id=blogtopic_id)
    if request.method != 'POST':
        form = BlogentryForm()
    else:
        form = BlogentryForm(request.POST, request.FILES)
        if form.is_valid():
            new_blogentry = form.save(commit=False)
            new_blogentry.blogtopic = blogtopic
            new_blogentry.blogentryowner = request.user
            new_blogentry.save()
            return HttpResponseRedirect(reverse('blog:blog'))
    context = {'blogtopic': blogtopic, 'form': form}
    return render(request, 'blog/new_blogentry.html', context)


# функция изменения статьи
@login_required
def edit_blogentry(request, blogentry_id):
    blogentry = Blogentry.objects.get(id=blogentry_id)
    blogtopic = blogentry.blogtopic
    if blogentry.blogentryowner != request.user:
        return render(request, 'learning_logs/notyours.html')
    if request.method != 'POST':
        form = BlogentryForm(instance=blogentry)
    else:
        form = BlogentryForm(instance=blogentry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blog:blogentry', args=[blogentry.id]))
    context = {'blogentry': blogentry, 'blogtopic': blogtopic, 'form': form}
    return render(request, 'blog/edit_blogentry.html', context)


# функция представления страницы статьи
@login_required
def blogentry(request, blogentry_id):
    blogentry = Blogentry.objects.get(id=blogentry_id)
    blogtopic = blogentry.blogtopic
    if request.user not in blogentry.bloglike.all():
        end = 'needtoadd'
    else:
        end = 'Данная статья уже добавлена в избранное'
    all_comments = Blogcomment.objects.filter(blogpost=blogentry).order_by('blogcreated')
    if request.method != 'POST':
        form = BlogcommentForm()
    else:
        form = BlogcommentForm(data=request.POST)
        if form.is_valid():
            blogcomment = form.save(commit=False)
            blogcomment.blogpost = blogentry
            blogcomment.blogname = request.user
            blogcomment.save()
            return HttpResponseRedirect(reverse('blog:blogentry', args=[blogentry_id]))

    context = {'blogentry': blogentry, 'blogtopic': blogtopic, 'form': form, 'all_comments': all_comments, 'end': end}
    return render(request, 'blog/blogentry.html', context)


# функция удаления статьи
def delete_blogentry(request, blogtopic_id, blogentry_id):
    blogentry = Blogentry.objects.get(id=blogentry_id)
    if blogentry.blogentryowner != request.user:
        return render(request, 'learning_logs/notyours.html')
    else:
        blogentry = Blogentry.objects.filter(id=blogentry_id)
        blogentry.delete()
    return HttpResponseRedirect(reverse('blog:blog'))


# функция добавления статьи в избранное
@login_required
def add_to_fav(request, blogentry_id):
    blogentry = Blogentry.objects.get(id=blogentry_id)
    if request.user not in blogentry.bloglike.all():
        blogentry.bloglike.add(request.user)
        end = 'needtoadd'
    else:
        end = 'Данная статья уже добавлена в избранное'
    return HttpResponseRedirect(reverse('blog:blogentry', args=[blogentry_id]))


# функция удаления статьи из избранного
@login_required
def remove_from_fav(request, blogentry_id):
    blogentry = Blogentry.objects.get(id=blogentry_id)
    if request.user in blogentry.bloglike.all():
        blogentry.bloglike.remove(request.user)
        end = ''
    else:
        end = 'Данная статья уже удалена из избранного'
    return HttpResponseRedirect(reverse('blog:blogfavourites'))


# функция представления страницы избранного
@login_required
def blogfavourites(request):
    blogfavourites = Blogentry.objects.filter(bloglike=request.user)
    read_more = '...продолжить читать статью'
    for fav in blogfavourites:
        if len(fav.blogtext) > 50:
            fav.blogtext = fav.blogtext[:50]
    context = {'blogfavourites': blogfavourites, 'read_more': read_more}
    return render(request, 'blog/blogfavourites.html', context)


# функция изменения комментария
@login_required
def edit_blogcomment(request, blogentry_id, blogcomment_id):
    blogcomment = Blogcomment.objects.get(id=blogcomment_id)
    blogentry = blogcomment.blogpost

    # all_comments = Comment.objects.filter(post=entry)
    # for comment in all_comments:
    if blogcomment.blogname != request.user:
        raise Http404
    else:
        if request.method != 'POST':
            form = BlogcommentForm(instance=blogcomment)
        else:
            form = BlogcommentForm(instance=blogcomment, data=request.POST)
            if form.is_valid():
                blogcomment.save()
                return HttpResponseRedirect(reverse('blog:blogentry', args=[blogentry_id]))
    context = {'blogcomment': blogcomment, 'blogentry': blogentry, 'form': form}
    return render(request, 'blog/edit_blogcomment.html', context)


# функция представления страницы всех статей определенного пользователя
@login_required
def alluserentries(request, user_id):
    alluserentries = Blogentry.objects.filter(blogentryowner=user_id).order_by('-blogdate_added')
    read_more = '...продолжить читать статью'
    for blogentry in alluserentries:
        blogtopic = blogentry.blogtopic
        id = blogtopic.id
        if len(blogentry.blogtext) > 50:
            blogentry.blogtext = blogentry.blogtext[:50]
    context = {'alluserentries': alluserentries, 'read_more': read_more, 'blogentry': blogentry, 'blogtopic': blogtopic,
               'id': id}
    return render(request, 'blog/alluserentries.html', context)


@login_required
def myentries(request, user_id):
    myentries = Blogentry.objects.filter(blogentryowner=user_id).order_by('-blogdate_added')
    read_more = '...продолжить читать статью'
    context = {'myentries': myentries, 'read_more': read_more}
    for blogentry in myentries:
        if blogentry.blogtext is not None:
            blogtopic = blogentry.blogtopic
            id = blogtopic.id
            context = {'myentries': myentries, 'read_more': read_more, 'blogentry': blogentry, 'blogtopic': blogtopic,
                       'id': id}
        if len(blogentry.blogtext) > 50:
            blogentry.blogtext = blogentry.blogtext[:50]

    return render(request, 'blog/myentries.html', context)
