from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%(value)s is not even number', params={'value': value})


class PollForm(forms.Form):
    title = forms.CharField(label='ชื่อโพล', max_length=100, required=True)
    email = forms.CharField(validators=[validators.validate_email])
    no_questions = forms.IntegerField(label='จำนวนคำถาม', min_value=0, max_value=10,
                                      required=True, validators=[validate_even])
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    # def clean_title(self):
    #     data = self.cleaned_data['title']
    #
    #     if 'ไอทีหมีแพนด้า' not in data:
    #         raise forms.ValidationError('คุณลืมชื่อคณะ')
    #
    #     return data

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and not end:
            # raise forms.ValidationError('โปรดเลือกวันที่สิ้นสุด')
            self.add_error('end_date', 'โปรดเลือกวันที่สิ้นสุด')

        if end and not start:
            # raise forms.ValidationError('โปรดเลือกวันที่เริ่มต้น')
            self.add_error('start_date', 'โปรดเลือกวันที่สิ้นสุด')


class CommentForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100, required=True)
    body = forms.CharField(label='body', widget=forms.Textarea, required=True)
    email = forms.CharField(label='Email', required=False, validators=[validators.validate_email])
    tel = forms.CharField(label='Mobile Number', max_length=10, required=False)

    def clean_tel(self):
        data = self.cleaned_data['tel']

        if data == '':
            return data

        if len(data) != 10:
            # raise forms.ValidationError('หมายเลขโทรศัพท์ต้องมี 10 หลัก')
            self.add_error('tel', 'หมายเลขโทรศัพท์ต้องมี 10 หลัก')

        if not data.isdigit():
            self.add_error('tel', 'หมายเลขโทรศัพท์ต้องเป็นตัวเลขเท่านั้น')
            # raise forms.ValidationError('หมายเลขโทรศัพท์ต้องเป็นตัวเลขเท่านั้น')
        return data

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        email = cleaned_data.get('email')
        tel = cleaned_data.get('tel')

        if not (email != "" or tel != ""):
            raise forms.ValidationError('ต้องกรอก email หรือ Mobile number')
