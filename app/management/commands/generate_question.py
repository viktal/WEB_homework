import random
from django.core.management.base import BaseCommand
from app.models import Question, Tag, User, Answer, Rating
from faker import Faker


def sample(elements, k):
    return random.sample(elements, k=k)


class Command(BaseCommand):
    def handle(self, counts_question, answers_per_question, *args, **options):
        fake = Faker()
        tags = list(Tag.objects.all())
        users = list(User.objects.all())

        questions = [Question(
                author=sample(users, 1)[0],
                title=fake.sentence(),
                text=fake.text(),
            ) for _ in range(counts_question)]
        questions = Question.objects.bulk_create(questions)
        questions = list(Question.objects.all())
        question_tags_relation = Question.tags.through
        relations = []

        for question in questions:
            relations.extend(question_tags_relation(question_id=question.id,
                                                    tag_id=tag.id) for tag in sample(tags, k=3))
        question_tags_relation.objects.bulk_create(relations)

        likes = sum([self.add_likes(q, users) for q in questions], [])
        Rating.objects.bulk_create(likes)

        answers = [[Answer(
            author=u, question=question, text=fake.text(), is_right=random.choice([True, False])
        ) for u in sample(users, random.randint(0, 20))]
            for question in questions]

        answers = sum(answers, [])
        Answer.objects.bulk_create(answers)

        answers = list(Answer.objects.all())

        likes = sum([self.add_likes(an, users) for an in answers], [])
        Rating.objects.bulk_create(likes)

    def add_likes(self, tolike, users, maxlikes=15):
        likes = random.randint(0, maxlikes)
        likes = min(likes, len(users))
        users = sample(users, likes)
        likes = [Rating(
                rate=random.choice([-1, 1]),
                author=user,
                content_object=tolike) for user in users]
        return likes
