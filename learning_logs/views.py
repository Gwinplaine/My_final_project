from django.shortcuts import render

from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry, Comment
from .forms import TopicForm, EntryForm, CommentForm


def index(request):
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    'выводит список тем'
    #    topics = Topic.objects.order_by('date_added')
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    read_more = '...продолжить читать статью'
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    for entry in entries:
        if len(entry.text) > 50:
            entry.text = entry.text[:50]
    context = {'topic': topic, 'entries':entries, 'read_more':read_more}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    '''определяет новую тему'''
    if request.method != 'POST':
        #данные не отправлялись, создаётся пустая форма.
        form = TopicForm()
    else:
        #отправлены данные POST; обработать данные
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('topics'))

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            if topic.owner != request.user:
                raise Http404
            new_entry.save()
            return  HttpResponseRedirect(reverse('topic', args=[topic_id]))
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('topic', args=[topic.id]))
    context = {'entry': entry, 'topic':topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

def entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    all_comments = Comment.objects.filter(active=True)
    if request.method != 'POST':
        form = CommentForm()
    else:
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = entry
            comment.name = request.user
            comment.save()
            return  HttpResponseRedirect(reverse('entry', args=[entry_id]))
    context = {'entry': entry, 'topic':topic, 'form':form, 'all_comments':all_comments}
    return render(request, 'learning_logs/entry.html', context)

