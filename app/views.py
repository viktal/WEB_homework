from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from app import forms

from app.models import Question, Answer, Tag, User, Rating

COUNT_OBJ_IN_PAGE = 10

# gunicorn --bind 127.0.0.1:8005 askme.wsgi
def app_wsgi(request):
    lines = ["Hello, world!"]

    for name, params in [("GET", request.GET), ("POST", request.POST)]:
        lines.append(f"{name} parameters: ")
        for key, value in params.items():
            lines.append(f"{key}:{value}")

    response_body = "<br>".join(lines)
    return HttpResponse(status=200, content=response_body.encode())


@login_required
def ask(request):
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


def question(request, qid):
    try:
        question = Question.objects.filter(pk=qid)
        if request.user.is_authenticated:
            question = Question.objects.annotate_user_rate(question, request.user)
        question = Question.objects.annotate_all(question).get()
    except Question.DoesNotExist:
        return HttpResponseNotFound("404 Not Found")

    answers_by_question = Answer.objects.filter(question=qid)
    answers = paginator(request, answers_by_question)
    answers.object_list = Answer.objects.annotate_currating(answers.object_list)
    if request.user.is_authenticated:
        answers.object_list = Answer.objects.annotate_user_rate(answers.object_list, request.user)

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
        return redirect(reverse('question', kwargs={'qid': question.pk}) + f'#{anchor}')
    ctx['form'] = form
    return render(request, 'question.html', ctx)


def tag(request, tag_name):
    questions = Question.objects.by_tag(tag_name)
    questions = paginator(request, questions)
    questions.object_list = Question.objects.annotate_all(questions.object_list)
    if request.user.is_authenticated:
        questions.object_list = Question.objects.annotate_user_rate(questions.object_list, request.user)
    return render(request, 'tag.html', {
        'page_obj': questions,
        'tag_name': tag_name,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def index(request):
    questions = Question.objects.all()
    questions = paginator(request, questions)
    questions.object_list = Question.objects.annotate_all(questions.object_list)
    if request.user.is_authenticated:
        questions.object_list = Question.objects.annotate_user_rate(questions.object_list, request.user)
    return render(request, 'index.html', {
        'page_obj': questions,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def like(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    else:
        like = Rating(
                object_id=int(request.POST['like-id']),
                content_type=ContentType.objects.get_for_model(Question),
                author=request.user,
                rate=1
        )
        like.save()
        return HttpResponse(status=200)


def dislike(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    else:
        dislike = Rating(
                object_id=int(request.POST['dislike-id']),
                content_type=ContentType.objects.get_for_model(Question),
                author=request.user,
                rate=-1
        )
        dislike.save()
        return HttpResponse(status=200)


def answer_like(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    else:
        like = Rating(
                object_id=int(request.POST['anlike-id']),
                content_type=ContentType.objects.get_for_model(Answer),
                author=request.user,
                rate=1
        )
        like.save()
        return HttpResponse(status=200)


def answer_dislike(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    else:
        dislike = Rating(
                object_id=int(request.POST['andislike-id']),
                content_type=ContentType.objects.get_for_model(Answer),
                author=request.user,
                rate=-1
        )
        dislike.save()
        return HttpResponse(status=200)


def answer_correct(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    else:
        id = (request.POST['correct-id'])[7:]
        answer = Answer.objects.get(pk=int(id))
        answer.is_right = True
        answer.save()
        return HttpResponse(status=200)


def hot(request):
    questions = Question.objects.hot()
    questions = paginator(request, questions)
    questions.object_list = Question.objects.annotate_all(questions.object_list)
    if request.user.is_authenticated:
        questions.object_list = Question.objects.annotate_user_rate(questions.object_list, request.user)
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


def logout(request):
    auth.logout(request)
    # Перенаправление на страницу.
    return redirect('/index')


def register(request):
    ctx = {'popular_tags': Tag.objects.popular(),
           'best_user': User.objects.best(),
           }
    if request.method == 'GET':
        form = forms.RegisterForm()
        ctx['form'] = form
        return render(request, 'register.html', ctx)
    form = forms.RegisterForm(data=request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = User.objects.create_user(username=username, email=email, password=password)
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/index')

    ctx['form'] = form
    return render(request, 'register.html', ctx)


@login_required
def settings(request):
    ctx = {'popular_tags': Tag.objects.popular(),
           'best_user': User.objects.best(),
           }
    user = request.user
    if request.method == 'GET':
        form = forms.UserForm(instance=request.user)
        ctx['form'] = form
        return render(request, 'settings.html', ctx)

    form = forms.UserForm(data=request.POST, files=request.FILES, instance=user)
    if form.is_valid() and form.has_changed():
        form.save()
    ctx['form'] = form
    return render(request, 'settings.html', ctx)


def paginator(request, objects):
    paginator = Paginator(objects, COUNT_OBJ_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
