from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app.models import Profile, Question, Answer, Tag


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput, max_length=16)


class RegisterForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ['nickname']

    def clean(self):
        super().clean()
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError('Passwords do not match!')
        return self.cleaned_data

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if User.objects.filter(username=nickname).exists():
            raise ValidationError('Nickname is taken!')
        return nickname

    def save(self, commit=True):
        data = self.cleaned_data

        user = User.objects.create_user(data['nickname'], data['email'], data['password'])

        profile = Profile.objects.create(user_id=user.id, nickname=data['nickname'])

        if commit:
            profile.save()
        return user


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        kwargs.update(initial={
            'email': self.user.email,
            'username': self.user.username,
        })
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.user.username and User.objects.filter(username=username).exists():
            raise ValidationError('Username already taken!')
        return username

    def save(self, commit=True):
        data = self.cleaned_data

        if data['username'] != self.user.username:
            self.user.username = data['username']
        self.user.email = data['email']

        self.user.profile.nickname = data['username']
        if data['avatar']:
            self.user.profile.avatar = data['avatar']

        if commit:
            self.user.save()
            self.user.profile.save()
        return self.user


class AskForm(forms.ModelForm):
    tags = forms.CharField(help_text='Write tags separated by comma',
                           required=False,
                           validators=[RegexValidator(regex=r'^[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*$',
                                                      message='Tags must contain only letters, digits and commas')])

    class Meta:
        model = Question
        fields = ['title', 'text']

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        data = self.cleaned_data
        question = Question.objects.create(title=data['title'], text=data['text'], author=self.profile)
        if data.get('tags', None) is not None:
            for tag in data['tags'].split(','):
                tag_from_db = Tag.objects.filter(name=tag)
                if not tag_from_db.exists():
                    tag_from_db = Tag.objects.create(name=tag)
                else:
                    tag_from_db = tag_from_db.first()
                question.tags.add(tag_from_db.id)
        if commit:
            question.save()
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        self.question = kwargs.pop('question')

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        data = self.cleaned_data
        ans = Answer.objects.create(author=self.profile, text=data['text'], question=self.question)
        if commit:
            ans.save()
        return ans
