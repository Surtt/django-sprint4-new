from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.constants import MODERATION_ERROR

from .models import Comment, Post
from .moderation import is_toxic

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')

        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}
            )
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        if is_toxic(text):
            raise ValidationError(MODERATION_ERROR)
        return text
