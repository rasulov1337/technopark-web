from json import JSONDecodeError

from django.contrib import auth
from django.contrib.auth import authenticate, login as django_auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse, resolve, Resolver404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from app.forms import RegisterForm, LoginForm, EditProfileForm, AskForm, AnswerForm
from app.models import *

import json

ANSWERS_PER_PAGE = 5


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


@require_GET
def index(request):
    page_object = paginate(Question.objects.new(), request)

    return render(request, 'index.html', {
        'questions': page_object
    })


@require_GET
def hot(request):
    page_object = paginate(Question.objects.hot(), request)

    return render(request, 'hot.html', {'questions': page_object})


@require_GET
def tag(request, tag_id):
    item = get_object_or_404(Tag, name=tag_id)
    page_object = paginate(Question.objects.by_tag(tag_id).order_by('created_date'), request)

    return render(request, 'tag.html', {
        'tag': tag_id,
        'questions': page_object,
        'answers': page_object,
    })


@csrf_protect
@require_http_methods(['GET', 'POST', 'DELETE'])
def question(request, question_id):
    item = get_object_or_404(Question, id=question_id)
    page_object = paginate(Answer.objects.filter(question=question_id), request, ANSWERS_PER_PAGE)

    if request.method == 'POST':
        if request.user.is_anonymous:
            return redirect('login') + '?continue=' + request.path
        ans_form = AnswerForm(profile=request.user.profile, question=item, data=request.POST)
        if ans_form.is_valid():
            ans = ans_form.save()

            if ans:  # TODO: перенести логику куда-нибудь
                curr_answer_index = 0
                for i in Answer.objects.filter(question=question_id):
                    if i.id == ans.id:
                        break
                    curr_answer_index += 1

                page = curr_answer_index // ANSWERS_PER_PAGE + 1

                return redirect(reverse('question', args=[item.id]) + '?page=' + str(page) + '#' + str(ans.id))
            else:
                ans_form.add_error(field=None, error='Answer saving error:')
    elif request.method == 'GET':
        ans_form = AnswerForm(profile=request.user, question=item)

    if request.method == 'GET' or request.method == 'POST':
        return render(request, 'question_details.html', {
            'question': item,
            'answers': page_object,
            'form': ans_form,
        })

    if request.method == 'DELETE':
        item.delete()
        return HttpResponse(status=204)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        try:
            redirect_page = request.GET.get('next', 'index')  # @login_required хранит URL в next
        except KeyError:
            redirect_page = request.GET.get('continue', 'index')

        try:
            resolve(redirect_page)
        except Resolver404:
            redirect_page = 'index'

        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user:
                django_auth_login(request, user)
                return redirect(redirect_page)
            else:
                login_form.add_error(None, 'Wrong username or password.')

    else:
        login_form = LoginForm()
    return render(request, 'login.html', {'form': login_form})


@csrf_protect
@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'GET':
        register_form = RegisterForm()
        return render(request, 'signup.html', {'form': register_form})

    # POST
    user_form = RegisterForm(data=request.POST)
    if user_form.is_valid():
        user = user_form.save()

        if user:
            auth.login(request, user)
            return redirect(reverse('index'))
        else:
            user_form.add_error(field=None, error='User saving error:')

    return render(request, 'signup.html', {'form': user_form})


@csrf_protect
@login_required
@require_http_methods(['GET', 'POST'])
def ask(request):
    if request.method == 'GET':
        form = AskForm()
        return render(request, 'ask.html', {'form': form})

    form = AskForm(data=request.POST, profile=request.user.profile)
    if form.is_valid():
        question = form.save()
        if question:
            return redirect(reverse('question', args=[question.id]))
        else:
            form.add_error(field=None, error='Ask saving error:')
    return render(request, 'ask.html', {'form': form})


@csrf_protect
@login_required
@require_http_methods(['GET', 'POST'])
def edit_profile(request):
    if request.method == 'GET':
        form = EditProfileForm(user=request.user)
        return render(request, 'settings.html', {'form': form})

    form = EditProfileForm(data=request.POST, user=request.user, files=request.FILES)
    if form.is_valid():
        profile = form.save()
        if profile:
            return redirect(reverse('edit-profile'))
        else:
            form.add_error(field=None, error='Profile saving error:')
    return render(request, 'settings.html', {'form': form})


@login_required
def logout(request):
    redirect_page = request.GET.get('continue', 'index')

    try:
        resolve(redirect_page)
    except Resolver404:
        redirect_page = 'index'

    auth.logout(request)
    return redirect(redirect_page)


@require_GET
def member(request, member_nickname):
    profile = get_object_or_404(Profile, nickname=member_nickname)
    return render(request, 'member.html', {'profile': profile})


@csrf_protect
@require_POST
def like_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        body = json.loads(request.body)
        question = get_object_or_404(Question, pk=body['questionId'])
    except JSONDecodeError:
        return JsonResponse({'error': 'Bad JSON'}, status=400)

    question.toggle_like(request.user.profile, 1 if body['isLike'] else -1)

    return JsonResponse({
        'score': question.score,
    })


@csrf_protect
@require_POST
def like_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
    except JSONDecodeError:
        return JsonResponse({'error': 'Bad JSON'}, status=400)

    answer.toggle_like(request.user.profile, 1 if body['isLike'] else -1)

    return JsonResponse({
        'score': answer.score,
    })


@csrf_protect
@require_POST
def mark_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
        question = get_object_or_404(Question, pk=body['questionId'])
    except KeyError or JSONDecodeError:
        return JsonResponse({'error': 'Bad JSON'}, status=400)

    if question.author.id != request.user.profile.id:
        return JsonResponse({'error': 'Only author of the question is able to mark answer as correct'}, status=403)

    answer.toggle_correct()
    return JsonResponse({'response': 'Marked'}, status=200)
