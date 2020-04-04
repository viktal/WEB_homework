from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpRequest

TEXT_PLACEHOLDER = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " \
                   "tempor incididunt ut labore et dolore magna aliqua. "

QUESTIONS = {
    i: {'id': i, 'title': f'How to write good code? : q # {i}',
        "body": TEXT_PLACEHOLDER * 3,
        "total_answers": i+1,
        "like": (i+15)*3,
        "tags": ['code', 'python', 'technopark']
        }
    for i in range(20)
}

tags = {
    i: {'id': i, 'title': f'How to write good code? : q # {i}',
        "body": TEXT_PLACEHOLDER * 3,
        "total_answers": i+1
        }
    for i in range(5)
}

answers = {
    i: {'id': i, 'title': f'answer # {i}',
        "body": TEXT_PLACEHOLDER * (i+1),
        }
    for i in range(3)
}

def question(request, qid):
    question = QUESTIONS.get(qid)
    answer = answers.values()
    return render(request, 'question.html', {
        'question': question,
        'answers': list(range(question['total_answers']))
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
        'questions': questions,
        'page_obj': questions,
        'tag_name': tag_name,
    })


def index(request):
    questions = listing(request, list(QUESTIONS.values()))
    return render(request, 'index.html', {
        'questions': questions,
        'page_obj': questions
    })

def hot(request):
    sort_q = sorted(QUESTIONS.values(), key=lambda like: like['like'], reverse=True)
    questions = listing(request, list(sort_q))
    return render(request, 'hot.html', {
        'questions': questions,
        'page_obj': questions,
    })


def login(request):
    return render(request, 'login.html', {})

def register(request):
    return render(request, 'register.html', {})

def settings(request):
    return render(request, 'settings.html', {})

def ask(request):
    return render(request, 'ask.html', {})


def listing(request, objects):
    paginator = Paginator(objects, 5)
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





#пагинация 2:05


# source vevn_/bin/activate
# python3.8 manage.py runserver
#
#


