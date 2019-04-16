from django import forms


class PollForm(forms.Form):
    title = forms.CharField(label='ชื่อโพล', max_length=100, required=True)
    no_question = forms.IntegerField(label='จำนวนคำถาม', min_value=0, max_value=10, required=True)
    start_date = forms.DateField()
    end_date = forms.DateField()
