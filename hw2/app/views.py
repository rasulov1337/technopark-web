import random

from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

# Create your views here.
QUESTIONS = [
    {
        "title": "Question %d" % i,
        "text": 'This is question number %d' % i,
        "id": i,
        'picture': '../static/img/cpp.png',
        'tags': ['tag0', 'cpp', 'tag' + str(i), 'tag' + str(i - 1)],
        'number_of_answers': random.randint(5, 9),
        'score': random.randint(-4, 4)
    } for i in range(1, 200)
]

ANSWERS = [
    {
        'text': 'Some answer text for number %d' % i,
        'picture': '../static/img/cpp.png',
        'score': random.randint(-3, 3)
    } for i in range(20)
]


def paginate(objects_list, request, per_page=5):
    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        page_num = 1

    paginator = Paginator(objects_list, per_page)

    if page_num >= paginator.num_pages:
        page_num = paginator.num_pages
    elif page_num < 1:
        page_num = 1

    page_object = paginator.page(page_num)

    return page_object


def index(request):
    page_object = paginate(QUESTIONS, request)

    return render(request, 'index.html', {'questions': page_object})


def hot(request):
    questions = list(reversed(QUESTIONS))
    page_object = paginate(questions, request)

    return render(request, 'hot.html', {'questions': page_object})


def tag(request, tag_id):
    questions = []
    for i in QUESTIONS:
        if i['tags'].count(tag_id):
            questions.append(i)

    page_object = paginate(questions, request)

    return render(request, 'tag.html', {'tag': tag_id, 'questions': page_object})


def question(request, question_id):
    item = QUESTIONS[question_id]

    page_object = paginate(ANSWERS, request)
    return render(request, 'question_details.html', {'question': item, 'answers': page_object})


def login(request):
    return render(request, 'login.html')


def signup(req):
    return render(req, 'signup.html')


def ask(req):
    return render(req, 'ask.html')


def settings(req):
    profile_info = {
        'avatar': '../static/img/avatar.png'
    }
    return render(req, 'settings.html', {'profile_info': profile_info})


def logout(req):
    return HttpResponse('Not working yet')
