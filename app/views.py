from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.http import HttpResponse
from django.db import models
from app import forms

from app.models import Question, Answer, Tag, User, Rating

COUNT_OBJ_IN_PAGE = 5



@login_required
def ask(request):
    # get - показать
    # post - переслать
    if request.method == 'GET':
        form = forms.QuestionForm(request.user)
        ctx = {'form': form}
        return render(request, 'ask.html', ctx)
    form = forms.QuestionForm(request.user, data=request.POST)
    if form.is_valid():
        question1 = form.save()
        return redirect(reverse('question', kwargs={'qid': question1.pk}))
    ctx = {'form': form}
    return render(request, 'ask.html', ctx)
    #     'popular_tags': popular_tags,
    #     'best_user': User.objects.best(),
    # })


def question(request, qid):
    question = get_object_or_404(Question, pk=qid)
    answers_by_question = Answer.objects.filter(question=qid)
    answers = listing(request, answers_by_question)

    if request.method == 'GET':
        form = forms.AnswerForm(request.user, question)
        ctx = {'form': form,
               'question': question,
               'page_obj': answers,
               'popular_tags': Tag.objects.popular(),
               'best_user': User.objects.best(),
               }
        return render(request, 'question.html', ctx)
    ctx = {'question': question,
           'page_obj': answers,
           'popular_tags': Tag.objects.popular(),
           'best_user': User.objects.best(),
           }
    if not request.user.is_authenticated:
        return redirect('/login')
    form = forms.AnswerForm(request.user, question, data=request.POST)
    if form.is_valid():
        answer = form.save()
        form = forms.AnswerForm(request.user, question)
        anchor = answer.pk
        ctx['form'] = form
        # return render(request, 'question.html', ctx)
        return redirect(reverse('question', kwargs={'qid': question.pk}) + f'#{anchor}')
        # return redirect('/question/%s#%s' % (question.pk, anchor))
        # return redirect(reverse('question2', kwargs={'qid': question.pk, 'anchor': answer.pk}))
    ctx['form'] = form
    return render(request, 'question.html', ctx)


def tag(request, tag_name):
    questions_by_tag = Question.objects.by_tag(tag_name)
    questions = listing(request, questions_by_tag)
    return render(request, 'tag.html', {
        'page_obj': questions,
        'tag_name': tag_name,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })

#
# def index(request):
#     questions = Question.objects.all()
#     questions = listing(request, questions)
#     return render(request, 'index.html', {
#         'page_obj': questions,
#         'popular_tags': Tag.objects.popular(),
#         'best_user': User.objects.best(),
#     })


def index(request):
    questions = Question.objects.all()
    questions = listing(request, questions)
    return render(request, 'ajax.html', {
        'page_obj': questions,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def like(request):
    #ВАЛИДАЦИЯ
    like = Rating(
            object_id=int(request.POST['like-id']),
            content_type=ContentType.objects.get_for_model(Question),
            author=request.user,
            rate=1
    )
    like.save()
    return HttpResponse(status=200)


def dislike(request):
    #ВАЛИДАЦИЯ
    dislike = Rating(
            object_id=int(request.POST['dislike-id']),
            content_type=ContentType.objects.get_for_model(Question),
            author=request.user,
            rate=-1
    )
    dislike.save()
    return HttpResponse(status=200)


# def ajax(request):
#     #ВАЛИДАЦИЯ
#     Question.objects.create(
#         author=request.user,
#         title='new{}'.format(request.POST.get('test-id')),
#         text='new_new'
#     )
#     return JsonResponse({'user': request.user.username,
#                          'question_count': Question.objects.count()})


def hot(request):
    # sort_q = sorted(QUESTIONS.values(), key=lambda like: like['like'], reverse=True)
    questions = listing(request, Question.objects.hot())
    return render(request, 'hot.html', {
        'page_obj': questions,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def login(request):
    if 'next' in request.GET:
        redirect_to = request.GET['next']
    else:
        redirect_to = request.META['HTTP_REFERER']

    ctx = {'redirect_to': redirect_to,
           'popular_tags': Tag.objects.popular(),
           'best_user': User.objects.best(),
           }

    if request.method == 'GET':
        form = forms.LoginForm()
        ctx['form'] = form

        return render(request, 'login.html', ctx)

    form = forms.LoginForm(data=request.POST)
    if form.is_valid():
        user = auth.authenticate(request, **form.cleaned_data)
        if user is not None:
            auth.login(request, user)
            return redirect(request.GET.get('next', '/index'))
        else:
            form.add_error('username', '')
            form.add_error('password', '')
    ctx['form'] = form
    return render(request, 'login.html', ctx)
    #     'popular_tags': Tag.objects.popular(),
    #     'best_user': User.objects.best(),
    # })


# https://stackoverflow.com/questions/45328826/django-model-fields-indexing
# class Meta:
#     indexes = [
#         models.Index(fields=['last_name', 'first_name']),
#         models.Index(fields=['first_name'], name='first_name_idx'),
#     ]


def logout(request):
    auth.logout(request)
    # Перенаправление на страницу.
    return redirect('/index')


def register(request):
    if request.method == 'GET':
        form = forms.RegisterForm()
        ctx = {'form': form}
        return render(request, 'register.html', ctx)
    form = forms.RegisterForm(data=request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = User.objects.create_user(username=username, email=email, password=password)
        user = auth.authenticate(request, **form.cleaned_data)
        if user is not None:
            auth.login(request, user)
            return redirect('/index')
        # return render(request, 'index.html')

    user = auth.authenticate(request, **form.cleaned_data)
    if user is not None:
        auth.login(request, user)
        return redirect('/index')
    ctx = {'form': form}
    return render(request, 'register.html', ctx)
    #     'popular_tags': popular_tags,
    #     'best_user': User.objects.best(),
    # })


@login_required
def settings(request):
    user = request.user
    if request.method == 'GET':
        form = forms.UserForm(instance=request.user)
        ctx = {'form': form}
        return render(request, 'settings.html', ctx)

    form = forms.UserForm(data=request.POST, instance=user)
    if form.is_valid() and form.has_changed():
        form.save()
    ctx = {'form': form}
    return render(request, 'settings.html', ctx)
    # ctx = {'form': form}
    # return render(request, 'settings.html', ctx)

    # return render(request, 'settings.html', {
    #     'popular_tags': popular_tags,
    #     'best_user': User.objects.best(),
    # })


# instance


def listing(request, objects):
    paginator = Paginator(objects, COUNT_OBJ_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
