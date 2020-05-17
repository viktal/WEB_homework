from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Subquery, OuterRef, Count
from django.utils import timezone


class TagManager(models.Manager):
    def popular(self, topk=10):
        return Tag.objects.annotate(counts=models.Count('qtags')).order_by("-counts")[:topk]


class QuestionManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        return qs

    def annotate_user_rate(self, qs, user):
        user_rate = Rating.objects.get_queryset() \
            .filter(object_id=OuterRef("pk"),
                    content_type=ContentType.objects.get_for_model(Question),
                    author=user) \
            .values('rate')
        qs = qs.annotate(
            user_rate=Subquery(user_rate)
        )
        return qs

    def annotate_answers_per_question(self, qs):
        answers_per_question = Answer.objects.get_rawqueryset() \
            .filter(question=OuterRef("pk")) \
            .values('question_id') \
            .annotate(c=Count("*")).values('c')
        qs = qs.annotate(
            count_answers=Subquery(answers_per_question)
        )
        return qs

    def annotate_currating(self, qs):
        currating = Rating.objects.get_queryset() \
            .filter(object_id=OuterRef("pk"), content_type=ContentType.objects.get_for_model(Question)) \
            .values('object_id') \
            .annotate(c=models.Sum('rate'))\
            .values('c')
        qs = qs.annotate(
            currating=Subquery(currating)
        )
        return qs
    
    def annotate_all(self, qs):
        qs = self.annotate_currating(qs)
        qs = self.annotate_answers_per_question(qs)
        return qs

    def hot(self):
        return self.get_queryset().order_by("-currating")

    def by_tag(self, tag_name):
        return super().get_queryset().prefetch_related('tags').filter(tags__title=tag_name)


class AnswerManager(models.Manager):
    def get_rawqueryset(self):
        return super().get_queryset()

    def annotate_user_rate(self, qs, user):
        user_rate = Rating.objects.get_queryset() \
            .filter(object_id=OuterRef("pk"),
                    content_type=ContentType.objects.get_for_model(Answer),
                    author=user) \
            .values('rate')
        qs = qs.annotate(
            user_rate=Subquery(user_rate)
        )
        return qs

    def annotate_currating(self, qs):
        currating = Rating.objects.get_queryset() \
            .filter(object_id=OuterRef("pk"), content_type=ContentType.objects.get_for_model(Answer)) \
            .values('object_id') \
            .annotate(c=models.Sum('rate'))\
            .values('c')
        qs = qs.annotate(
            currating=Subquery(currating)
        )
        return qs


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
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['author']),
        ]
        constraints = [
            models.UniqueConstraint(fields=('object_id', 'content_type', 'author'),
                                    name="one user - one rating")
        ]


class Question(models.Model):
    objects = QuestionManager()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quser')
    title = models.CharField(max_length=120, verbose_name="Title")
    text = models.TextField(verbose_name="Text")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Time")
    is_active = models.BooleanField(default=True, verbose_name="Availability")

    ratings = GenericRelation(Rating)
    tags = models.ManyToManyField(Tag, blank=True, related_name='qtags')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-create_date']
        indexes = [
            models.Index(fields=['is_active']),
            # models.Index(fields=['tags']),
            # models.Index(fields=['-ratings']),
        ]


class Answer(models.Model):
    objects = AnswerManager()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Your answer")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Creation time")
    is_right = models.BooleanField(default=False)
    ratings = GenericRelation(Rating)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-create_date']
        # indexes = [
        #     models.Index(fields=['question', 'ratings']),
        # ]
