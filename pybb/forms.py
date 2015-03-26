# coding: utf-8
from django import forms

from pybb.models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']


class TopicForm(forms.Form):
    name = forms.CharField(label=u'Topic Title')
    content = forms.CharField(label=u'Message', widget=forms.Textarea(attrs={'cols':None}))


class TopicDeleteForm(forms.Form):
    pass
