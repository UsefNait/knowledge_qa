from qa.models import *
from django.contrib.auth.models import User
from django import forms
from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget
from markdownx.fields import MarkdownxFormField
from ckeditor_uploader.fields import RichTextUploadingField

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = '__all__'