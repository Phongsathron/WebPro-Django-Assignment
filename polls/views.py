from django.db.models import Count
# from django.http import HttpResponse
from django.shortcuts import render

from polls.forms import PollForm
from polls.models import Poll, Question, Answer


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


def create(request):
    if request.method == 'POST':
        form = PollForm(request.POST)

        if form.is_valid():
            poll = Poll.objects.create(
                title=form.cleaned_data.get('title'),
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date')
            )

            for i in range(1, form.cleaned_data.get('no_question')+1):
                Question.objects.create(
                    text='0000' + str(i),
                    type='01',
                    poll=poll
                )
    else:
        form = PollForm()

    context = {'form': form}
    return render(request, 'polls/create.html', context=context)
