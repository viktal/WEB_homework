from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.shortcuts import render, get_object_or_404

from app.models import Question, Answer, Tag, User

COUNT_OBJ_IN_PAGE = 20

TEXT_PLACEHOLDER = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " \
                   "tempor incididunt ut labore et dolore magna aliqua. "

popular_tags = ['code', 'python', 'technopark', 'mail.ru', 'django', 'c++', 'web', 'google']

QUESTIONS = {
    i: {'id': i, 'title': f'How to write good code? : q # {i}',
        "body": TEXT_PLACEHOLDER * 3,
        "total_answers": i+1,
        "like": (i+15)*3,
        "tags": list(set(random.choices(popular_tags, k=3)))
        }
    for i in range(100)
}

def question(request, qid):
    question = get_object_or_404(Question, pk=qid)
    answers_by_question = Answer.objects.filter(question=qid)
    answers = listing(request, answers_by_question)
    return render(request, 'question.html', {
        'question': question,
        'page_obj': answers,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def tag(request, tag_name):
    questions_by_tag = Question.objects.by_tag(tag_name)
    # for q in QUESTIONS.values():
    #     for q_tag in q['tags']:
    #         if q_tag == tag_name:
    #             result.append(q)
    #             break
    questions = listing(request, questions_by_tag)
    return render(request, 'tag.html', {
        'page_obj': questions,
        'tag_name': tag_name,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def index(request):
    questions = Question.objects.all()
    questions = listing(request, questions)
    return render(request, 'index.html', {
        'page_obj': questions,
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def hot(request):
    # sort_q = sorted(QUESTIONS.values(), key=lambda like: like['like'], reverse=True)
    # questions = listing(request, sort_q)
    return render(request, 'hot.html', {
        'page_obj': Question.objects.hot(),
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


def login(request):
    return render(request, 'login.html', {
        'popular_tags': Tag.objects.popular(),
        'best_user': User.objects.best(),
    })


# https://stackoverflow.com/questions/45328826/django-model-fields-indexing
    # class Meta:
    #     indexes = [
    #         models.Index(fields=['last_name', 'first_name']),
    #         models.Index(fields=['first_name'], name='first_name_idx'),
    #     ]


def register(request):
    return render(request, 'register.html', {
        'popular_tags': popular_tags,
        'best_user': User.objects.best(),
    })


def settings(request):
    return render(request, 'settings.html', {
        'popular_tags': popular_tags,
        'best_user': User.objects.best(),
    })


def ask(request):
    return render(request, 'ask.html', {
        'popular_tags': popular_tags,
        'best_user': User.objects.best(),
    })


def listing(request, objects):
    paginator = Paginator(objects, COUNT_OBJ_IN_PAGE)
    # page = request.GET.get('page')
    # try:
    #     contacts = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     contacts = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     contacts = paginator.page(paginator.num_pages)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

