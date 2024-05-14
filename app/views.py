from json import JSONDecodeError

from django.contrib import auth
from django.contrib.auth import authenticate, login as django_auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse, resolve, Resolver404
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
        'questions': page_object,
    })


@require_GET
def hot(request):
    page_object = paginate(Question.objects.hot(), request)

    return render(request, 'hot.html', {'questions': page_object})


@require_GET
def tag(request, tag_id):
    item = get_object_or_404(Tag, name=tag_id)
    page_object = paginate(Question.objects.by_tag(tag_id), request)

    return render(request, 'tag.html', {
        'tag': tag_id,
        'questions': page_object,
        'answers': page_object,
    })


@require_http_methods(['GET', 'POST'])
def question(request, question_id):
    item = get_object_or_404(Question, id=question_id)
    page_object = paginate(Answer.objects.filter(question=question_id), request, ANSWERS_PER_PAGE)

    if request.method == 'POST' and request.user.is_authenticated:
        ans_form = AnswerForm(profile=request.user.profile, question=item, data=request.POST)
        if ans_form.is_valid():
            ans = ans_form.save()

            if ans:
                curr_answer_index = 0
                for i in Answer.objects.filter(question=question_id):
                    if i.id == ans.id:
                        break
                    curr_answer_index += 1

                page = curr_answer_index // ANSWERS_PER_PAGE + 1

                return redirect(reverse('question', args=[item.id]) + '?page=' + str(page) + '#' + str(ans.id))
            else:
                ans_form.add_error(field=None, error='Answer saving error:')
    else:
        ans_form = AnswerForm(profile=request.user, question=item)

    return render(request, 'question_details.html', {
        'question': item,
        'answers': page_object,
        'form': ans_form,
    })


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


@login_required
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


@require_POST
def like_question(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    try:
        body = json.loads(request.body)
        question = get_object_or_404(Question, pk=body['questionId'])
        profile = get_object_or_404(Profile, id=request.user.profile.id)
    except JSONDecodeError:
        return HttpResponseBadRequest('Bad JSON')

    question_like = QuestionLike.objects.filter(question=question, author=profile)
    score_delta = 1 if body['isLike'] else -1

    if question_like.exists() and question_like.first().status == score_delta:
        return HttpResponse('Already Liked/Disliked', status=409)

    if question_like.exists():
        question.score -= question_like.first().status
        question_like.delete()

    question_like = QuestionLike.objects.create(author=profile, question=question, status=score_delta)
    question_like.save()

    question.score += score_delta
    question.save()
    return JsonResponse({
        'score': question.score,
    })


@require_POST
def like_answer(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
        profile = get_object_or_404(Profile, id=request.user.profile.id)
    except JSONDecodeError:
        return HttpResponseBadRequest('Bad JSON')

    answer_like = AnswerLike.objects.filter(answer=answer, author=profile)
    score_delta = 1 if body['isLike'] else -1

    if answer_like.exists() and answer_like.first().status == score_delta:
        return HttpResponse('Already Liked/Disliked', status=409)

    if answer_like.exists():
        answer.score -= answer_like.first().status
        answer_like.delete()

    answer_like = AnswerLike.objects.create(author=profile, answer=answer, status=score_delta)
    answer_like.save()

    answer.score += score_delta
    answer.save()
    return JsonResponse({
        'score': answer.score,
    })


@require_POST
def mark_answer(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    try:
        body = json.loads(request.body)
        answer = get_object_or_404(Answer, pk=body['answerId'])
        question = get_object_or_404(Question, pk=body['questionId'])
        is_correct = body['isCorrect']
    except KeyError or JSONDecodeError:
        return HttpResponseBadRequest('Bad JSON')

    if question.author.id != request.user.profile.id:
        return HttpResponseBadRequest('Only author of the question is able to mark answer as correct')

    answer.status = 'A' if is_correct else 'S'
    answer.save()
    return HttpResponse('Marked', status=200)
