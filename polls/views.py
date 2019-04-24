import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core import serializers
from django.db import IntegrityError
from django.db.models import Count
# from django.http import HttpResponse
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

from polls.forms import PollForm, CommentForm, ChangePasswordForm, RegisterForm, PollModelForm, QuestionForm, \
    ChoiceModelForm, CommentModelForm
from polls.models import Poll, Question, Answer, Choice, Comment, Profile


# Create your views here.

def index(request):
    poll_list = Poll.objects.annotate(question_count=Count('question'))
    # poll_list = Poll.objects.all()

    # for poll in poll_list:
    #     poll.question_count = Question.objects.filter(poll_id=poll.id).count()

    context = {
        'page_title': 'My Polls',
        'poll_list': poll_list
    }

    return render(request, 'polls/index.html', context=context)

    # return HttpResponse("Hello World, welcome to your first view")


@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):

    poll_detail = Poll.objects.get(pk=poll_id)

    if request.method == 'POST':
        for question in poll_detail.question_set.all():
            name = 'choice' + str(question.id)
            choice_id = request.POST.get(name)

            if choice_id:
                try:
                    ans = Answer.objects.get(question_id=question.id)
                    ans.choice_id = choice_id
                    ans.save()
                except Answer.DoesNotExist:
                    Answer.objects.create(
                        choice_id=choice_id,
                        question_id=question.id
                    )

            print(choice_id)

    context = {
        'poll': poll_detail
    }

    return render(request, 'polls/detail.html', context=context)

    # return HttpResponse("%s" % context)
    # return HttpResponse("This is a poll detail of %d" % poll_id)


@login_required
@permission_required('polls.add_poll')
def create(request):
    context = {}
    question_form_set = formset_factory(QuestionForm, extra=2)
    if request.method == 'POST':
        form = PollModelForm(request.POST)
        formset = question_form_set(request.POST)

        if form.is_valid():
            poll = form.save()

            if formset.is_valid():
                for question_form in formset:
                    Question.objects.create(
                        text=question_form.cleaned_data.get('text'),
                        type=question_form.cleaned_data.get('type'),
                        poll=poll
                    )
                context['success'] = 'Poll %s is created successfully!' %poll.title

    else:
        form = PollModelForm()
        formset = question_form_set()

    context['form'] = form
    context['formset'] = formset

    return render(request, 'polls/create.html', context=context)

@login_required
@permission_required('polls.change_poll')
def update(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)

    if request.method == 'POST':
        form = PollModelForm(request.POST, instance=poll)
        formset = QuestionFormSet(request.POST)

        if form.is_valid():
            form.save()
            if formset.is_valid():
                for question_form in formset:
                    if question_form.cleaned_data.get('question_id'):
                        question = Question.objects.get(id=question_form.cleaned_data.get('question_id'))
                        if question:
                            question.text = question_form.cleaned_data.get('text')
                            question.type = question_form.cleaned_data.get('type')
                            question.save()
                    else:
                        if question_form.cleaned_data.get('text'):
                            Question.objects.create(
                                text=question_form.cleaned_data.get('text'),
                                type=question_form.cleaned_data.get('type'),
                                poll=poll
                            )
                return redirect('poll_update', poll_id=poll.id)

    else:
        form = PollModelForm(instance=poll)

        data = []
        for question in poll.question_set.all():
            data.append(
                {
                    'text': question.text,
                    'type': question.type,
                    'question_id': question.id
                }
            )

            formset = QuestionFormSet(initial=data)

    context = {
        'form': form,
        'formset': formset,
        'poll': poll
    }

    return render(request, 'polls/update.html', context=context)


def createAnswer(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)

    if request.method == 'POST':
        question = Question.objects.create(
            text=request.POST.get('title'),
            type='01',
            poll=poll
        )

        for i in range(1, int(request.POST.get('no_questions'))+1):
            Choice.objects.create(
                text=request.POST.get('choice{}'.format(i)),
                value=request.POST.get('value{}'.format(i)),
                question=question
            )

        return redirect('index')

    context = {'poll': poll}

    return render(request, 'polls/create_answers.html', context=context)


def mylogin(request):

    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password'

    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url

    return render(request, 'polls/login.html', context=context)


def mylogout(request):
    logout(request)
    return redirect('login')


def createComment(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)

    if request.method == 'POST':
        form = CommentModelForm(request.POST)

        if form.is_valid():
            Comment.objects.create(
                title=form.cleaned_data.get('title'),
                body=form.cleaned_data.get('body'),
                email=form.cleaned_data.get('email'),
                tel=form.cleaned_data.get('tel'),
                poll=poll
            )

            return redirect('poll_detail', poll_id=poll_id)

    else:
        form = CommentModelForm()

    context = {
        'form': form,
        'poll': poll
    }

    return render(request, 'polls/create_comment.html', context=context)


@login_required
def changePassword(request):
    context = {}

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            if check_password(form.cleaned_data.get('old_password'), request.user.password):
                request.user.set_password(form.cleaned_data.get('new_password'))
                request.user.save()
                context['success'] = True
                context['message'] = None
            else:
                context['success'] = False
                context['message'] = 'รหัสผ่านไม่ถูกต้อง'
    else:
        form = ChangePasswordForm()

    context['form'] = form

    return render(request, 'polls/change_password.html', context=context)


def register(request):
    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            try:
                user = User.objects.create(
                    username=form.cleaned_data.get('username'),
                    email=form.cleaned_data.get('email'),
                    password=form.cleaned_data.get('password')
                )

                profile = Profile.objects.create(
                    user=user,
                    line_id=form.cleaned_data.get('line_id'),
                    facebook=form.cleaned_data.get('facebook'),
                    gender=form.cleaned_data.get('sex'),
                    birthdate=form.cleaned_data.get('birthdate')
                )

                context['success'] = True
                context['message'] = 'สมัครสมาชิกเรียบร้อยแล้ว'

            except IntegrityError:
                context['success'] = False
                context['message'] = 'มีผุ้ใช้งานนี้ในระบบอยู่แล้ว'

    else:
        form = RegisterForm()

    context['form'] = form

    return render(request, 'polls/register.html', context=context)

@login_required()
@permission_required('poll.change_poll')
def delete_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.delete()
    return redirect('poll_update', poll_id=question.poll.id)

@login_required()
@permission_required('poll.change_poll')
def add_choice(request, question_id):
    question = Question.objects.get(id=question_id)
    context = {'question': question}

    return render(request, 'choices/add.html', context=context)


def update_choice(request, question_id):
    question = Question.objects.get(id=question_id)
    context = {'question': question}

    return render(request, 'choices/update.html', context=context)


def add_choice_api(request, question_id):
    if request.method == 'POST':
        choice_list = json.loads(request.body)
        error_list = []

        for choice in choice_list:
            data = {
                'text': choice['text'],
                'value': choice['value'],
                'question': question_id
            }

            form = ChoiceModelForm(data)
            if form.is_valid():
                form.save()
            else:
                error_list.append(form.errors.as_text())
        if len(error_list) == 0:
            return JsonResponse({'message': 'success'}, status=200)
        else:
            return JsonResponse({'message': error_list}, status=400)

    return JsonResponse({'message': 'This API does not accept GET request.'}, status=405)


def get_choices_api(request, question_id):
    question = Question.objects.get(id=question_id)
    choice = serializers.serialize('json', question.choice_set.all())
    print(json.loads(choice))

    return JsonResponse({'choices': json.loads(choice)})


def update_choice_api(request, question_id):
    if request.method == 'POST':
        choice_list = json.loads(request.body)
        error_list = []

        for choice in choice_list:
            data = {
                'text': choice['text'],
                'value': choice['value'],
                'question': question_id
            }
            if 'id' in choice:
                choice = Question.objects.get(id=question_id).choice_set.get(id=choice['id'])
                form = ChoiceModelForm(data, instance=choice)
                if form.is_valid():
                    form.save()
                else:
                    error_list.append(form.errors.as_text())
            else:
                choice = Choice.objects.create(
                    text=data['text'],
                    value=data['value'],
                    question=Question.objects.get(id=question_id)
                )

        if len(error_list) == 0:
            return JsonResponse({'message': 'success'}, status=200)
        else:
            return JsonResponse({'message': error_list}, status=400)

    return JsonResponse({'message': 'This API does not accept GET request.'}, status=405)


def delete_choice_api(request, choice_id):
    if request.method == 'POST':
        error_list = []

        choice = Choice.objects.get(id=choice_id)
        choice.delete()

        return JsonResponse({'message': 'success'}, status=200)

    return JsonResponse({'message': 'This API does not accept GET request.'}, status=405)
