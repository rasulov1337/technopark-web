from django.contrib.auth.models import User
from django.db import models
from datetime import date
from django.db.models import Count, Sum


# Create your models here.

class QuestionManager(models.Manager):
    def hot(self):
        return self.all().order_by('-score', '-answers_counter', 'title')

    def new(self):
        return self.all().order_by('-created_date')

    def by_tag(self, tag: str):
        return self.filter(tags__name=tag)


class ProfileManager(models.Manager):
    def best(self):
        return self.all().order_by('-score')[:5]

    def get_by_nickname(self, nickname):
        return self.get(nickname=nickname)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='images')
    nickname = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    answers_counter = models.IntegerField(default=0)
    questions_counter = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    objects = ProfileManager()

    def __str__(self):
        return self.nickname


class TagManager(models.Manager):
    def popular(self):
        return self.all().order_by('-questions_counter')[:5]


class Tag(models.Model):
    name = models.CharField(max_length=30)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    questions_counter = models.IntegerField(default=0)

    objects = TagManager()

    def __str__(self):
        return self.name


class Question(models.Model):
    STATUS_CHOICES = (('S', 'Solved'), ('N', 'Not Solved'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    text = models.CharField(max_length=300)
    tags = models.ManyToManyField(Tag, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    answers_counter = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title + ' ' + self.get_status_display()


class Answer(models.Model):
    STATUS_CHOICES = (('S', 'Suggested'), ('A', 'Accepted'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    text = models.CharField(max_length=200)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.text + ' ' + self.get_status_display()


class QuestionLikeManager(models.Manager):
    def get_likes_counter(self, question_id):
        return self.filter(question__question=question_id)


class QuestionLike(models.Model):
    STATUS_CHOICES = ((-1, 'Disliked'), (1, 'Liked'))
    status = models.IntegerField(choices=STATUS_CHOICES)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = QuestionLikeManager()

    def __str__(self):
        return str(self.author) + ' ' + self.get_status_display()

    class Meta:
        unique_together = ('author', 'question')


class AnswerLike(models.Model):
    STATUS_CHOICES = ((-1, 'Disliked'), (1, 'Liked'))
    status = models.IntegerField(choices=STATUS_CHOICES)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    answer = models.ForeignKey(Answer, null=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.author) + ' ' + self.get_status_display()

    class Meta:
        unique_together = ('author', 'answer')
