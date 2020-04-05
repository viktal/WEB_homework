from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random

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
    question = QUESTIONS.get(qid)
    return render(request, 'question.html', {
        'question': question,
        'answers': list(range(question['total_answers'])),
        'popular_tags': popular_tags,
    })


def tag(request, tag_name):
    result = []
    for q in QUESTIONS.values():
        for q_tag in q['tags']:
            if q_tag == tag_name:
                result.append(q)
                break
    questions = listing(request, result)
    return render(request, 'tag.html', {
        'page_obj': questions,
        'tag_name': tag_name,
        'popular_tags': popular_tags,
    })


def index(request):
    questions = listing(request, list(QUESTIONS.values()))
    return render(request, 'index.html', {
        'page_obj': questions,
        'popular_tags': popular_tags,
    })


def hot(request):
    sort_q = sorted(QUESTIONS.values(), key=lambda like: like['like'], reverse=True)
    questions = listing(request, sort_q)
    return render(request, 'hot.html', {
        'page_obj': questions,
        'popular_tags': popular_tags,
    })


def login(request):
    return render(request, 'login.html', {
        'popular_tags': popular_tags,
    })


def register(request):
    return render(request, 'register.html', {
        'popular_tags': popular_tags,
    })


def settings(request):
    return render(request, 'settings.html', {
        'popular_tags': popular_tags,
    })


def ask(request):
    return render(request, 'ask.html', {
        'popular_tags': popular_tags,
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

# source vevn_/bin/activate
# python3.8 manage.py runserver
