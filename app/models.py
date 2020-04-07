from __future__ import unicode_literals
from datetime import datetime
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class TagManager(models.Manager):
    def popular(self, topk=10):
        return Tag.objects.annotate(counts=models.Count('qtags')).order_by("-counts")[:topk]


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).prefetch_related('ratings').\
            annotate(currating=models.Sum('ratings__rate'))

    def hot(self):
        return self.get_queryset().order_by("-currating")

    def by_tag(self, tag_name):
        return super().get_queryset().prefetch_related('tags').filter(tags__title=tag_name)


class AnswerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('ratings')\
            .annotate(currating=models.Sum('ratings__rate'))


class MyUserManager(UserManager):
    def best(self, topk=5):
        return User.objects.annotate(counts=models.Count('quser')).order_by("-counts")[:topk]


class Tag(models.Model):
    objects = TagManager()
    title = models.CharField(max_length=120, verbose_name="Tag title")

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('title',), name="no title dups")
        ]
        indexes = [
            models.Index(fields=('title',))
        ]


class User(AbstractUser):
    objects = MyUserManager()
    avatar = models.ImageField(upload_to='img/', default='cat.jpg')

    def __str__(self):
        return self.username


class Rating(models.Model):
    CHOICES = (
        (-1, "Dislike"),
        (1, "Like")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.SmallIntegerField(choices=CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['object_id', 'content_type', 'author']),
        ]
        constraints = [
            models.UniqueConstraint(fields=('object_id', 'content_type', 'author'), name="one user - one rating")
        ]


class Question(models.Model):
    objects = QuestionManager()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quser')
    title = models.CharField(max_length=120, verbose_name="Заголовок вопроса")
    text = models.TextField(verbose_name="Полное описание вопроса")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Время создания вопроса")
    is_active = models.BooleanField(default=True, verbose_name="Доступность вопроса")

    ratings = GenericRelation(Rating)
    tags = models.ManyToManyField(Tag, blank=True, related_name='qtags')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-create_date']
        indexes = [
            models.Index(fields=['is_active']),
        ]


class Answer(models.Model):
    objects = AnswerManager()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name=u"Полное описание ответа")
    create_date = models.DateTimeField(default=timezone.now, verbose_name=u"Время создания")
    is_right = models.BooleanField(default=True, verbose_name=u"Правильность ответа")
    ratings = GenericRelation(Rating)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-create_date']

        indexes = [
            models.Index(fields=['question']),
        ]
