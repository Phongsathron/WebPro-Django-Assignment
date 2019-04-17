from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
# from django.http import HttpResponse
from django.shortcuts import render, redirect

from polls.forms import PollForm, CommentForm, ChangePasswordForm, RegisterForm
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
    if request.method == 'POST':
        form = PollForm(request.POST)

        if form.is_valid():
            poll = Poll.objects.create(
                title=form.cleaned_data.get('title'),
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date')
            )

            # for i in range(1, form.cleaned_data.get('no_questions')+1):
            #     Question.objects.create(
            #         text='0000' + str(i),
            #         type='01',
            #         poll=poll
            #     )

            return redirect('create_answer', poll_id=poll.id)

    else:
        form = PollForm()

    context = {
        'form': form,
    }

    return render(request, 'polls/create.html', context=context)


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
        form = CommentForm(request.POST)

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
        form = CommentForm()

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

