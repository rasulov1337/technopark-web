import random

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from app.models import *


# Create your views here.

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
    page_object = paginate(Question.objects.all(), request)

    return render(request, 'index.html', {
        'questions': page_object,
    })


def hot(request):
    page_object = paginate(Question.objects.hot(), request)

    return render(request, 'hot.html', {'questions': page_object})


def tag(request, tag_id):
    item = get_object_or_404(Tag, name=tag_id)
    page_object = paginate(Question.objects.by_tag(tag_id), request)

    return render(request, 'tag.html', {
        'tag': tag_id,
        'questions': page_object,
        'answers': page_object,
    })


def question(request, question_id):
    item = get_object_or_404(Question, id=question_id)

    page_object = paginate(Answer.objects.filter(question=question_id), request)
    return render(request, 'question_details.html', {
        'question': item,
        'answers': page_object
    })


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


def member(req, member_nickname):
    profile = get_object_or_404(Profile, nickname=member_nickname)
    return render(req, 'member.html', {'profile': profile})
