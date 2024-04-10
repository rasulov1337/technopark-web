import random
import time

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Sum

from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

MIN_NUM_OF_TAGS = 1
MAX_NUM_OF_TAGS = 10

LIKE = 1
DISLIKE = -1
LIKE_STATUS_CHOICE = DISLIKE, LIKE


class Command(BaseCommand):
    help = 'Fills the database with test data based on the given ratio.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='The fill ratio for test data')

    def del_old_data(self):
        self.stdout.write(self.style.WARNING('Deleting old data from DB'))
        Tag.objects.all().delete()
        AnswerLike.objects.all().delete()
        QuestionLike.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()

    def generate_users_and_profiles(self, ratio: int):
        # Users
        django_users = [User(username='user %d' % i, email='user%d@%d.com' % (i, i), password='qwerty123')
                        for i in range(ratio)]
        User.objects.bulk_create(django_users)

        # Profiles
        last_time = time.time()
        user_profiles = [Profile(user=user, nickname='johndoe%i' % i)
                         for i, user in enumerate(django_users)]
        Profile.objects.bulk_create(user_profiles, batch_size=100)

    def generate_tags(self, ratio: int):
        tags = [Tag(name=f"Tag {i}") for i in range(ratio)]
        Tag.objects.bulk_create(tags, batch_size=100)

    def generate_questions(self, profiles, ratio: int):
        questions = [Question(title='Lorem ipsum dolor %d' % i,
                              text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean finibus libero non arcu bibendum tincidunt. Nam consequat facilisis condimentum. Phasellus non turpis ut enim condimentum convallis a ut odio. Phasellus volutpat enim leo, sit amet vestibulum sapien finibus non. Morbi tristique vivamus.""",
                              author=random.choice(profiles)) for i in range(ratio * 10)]
        Question.objects.bulk_create(questions, batch_size=100)

    def tie_tags_and_questions(self, tags, questions):
        list_of_random_tags_list = [
            random.sample(tags, min(len(tags), random.randint(MIN_NUM_OF_TAGS, MAX_NUM_OF_TAGS))) for _ in
            range(10)]

        for question in questions:
            question.tags.add(*random.choice(list_of_random_tags_list))

    def generate_answers(self, profiles, questions, ratio):
        answers = []
        for i in range(ratio * 100):
            author = random.choice(profiles)
            answers.append(Answer(text='Okay. It is very simple %d' % i, author=author,
                                  question=random.choice(questions)))
        Answer.objects.bulk_create(answers, batch_size=100)

    def generate_answerlikes(self, profiles, answers, ratio):
        answerlikes = []
        used_pairs = set()
        i = 0
        while i != (ratio * 100):
            user = random.choice(profiles)
            answer = random.choice(answers)
            pair = (user, answer)
            if pair not in used_pairs:
                status = random.choice(LIKE_STATUS_CHOICE)
                answerlikes.append(AnswerLike(author=user,
                                              answer=answer,
                                              status=status))
                used_pairs.add(pair)
                i += 1
        AnswerLike.objects.bulk_create(answerlikes, batch_size=100)

    def generate_questionlikes(self, profiles, questions, ratio):
        questionlikes = []
        used_pairs = set()
        i = 0
        while i != (ratio * 100):
            author = random.choice(profiles)
            question = random.choice(questions)
            pair = (author, question)
            if pair not in used_pairs:
                questionlikes.append(QuestionLike(author=author,
                                                  question=question,
                                                  status=random.choice(LIKE_STATUS_CHOICE)))
                used_pairs.add(pair)
                i += 1

        QuestionLike.objects.bulk_create(questionlikes, batch_size=100)

    def handle(self, *args, **kwargs):
        script_start_time = time.time()
        last_time = time.time()

        # Clear old data
        self.del_old_data()
        print('Successfully deleted old data from DB', time.time() - last_time)

        # Begin the generation
        ratio = kwargs['ratio']

        # Users and Profiles
        last_time = time.time()
        self.generate_users_and_profiles(ratio)

        profiles = list(Profile.objects.all())
        print('Successfully filled profiles', time.time() - last_time)

        # Creation of Tags
        last_time = time.time()
        self.generate_tags(ratio)
        tags = list(Tag.objects.all())
        print('Successfully filled tags', time.time() - last_time)

        # Questions
        last_time = time.time()
        self.generate_questions(profiles, ratio)
        questions = list(Question.objects.all())
        print('Successfully filled questions', time.time() - last_time)

        # Tie tags to questions
        last_time = time.time()
        self.tie_tags_and_questions(tags, questions)
        print('Successfully tied tags to questions', time.time() - last_time)

        # QuestionLikes
        last_time = time.time()
        self.generate_questionlikes(profiles, questions, ratio)
        print('Successfully filled question likes', time.time() - last_time)

        # Answers
        last_time = time.time()
        self.generate_answers(profiles, questions, ratio)
        print('Successfully filled answers ', time.time() - last_time)

        # AnswerLikes
        answers = list(Answer.objects.all())
        last_time = time.time()
        self.generate_answerlikes(profiles, answers, ratio)
        print('Successfully filled answer likes', time.time() - last_time)

        # Update fields

        # Question
        questions = Question.objects.all()
        updated_questions = []
        for i in questions:
            questionlikes = QuestionLike.objects.filter(question=i)
            new_score = questionlikes.aggregate(Sum('status')).get('status__sum', 0)
            new_answers_counter = Answer.objects.filter(question=i).count()
            if i.score == new_score and i.answers_counter == new_answers_counter:
                continue
            if new_score is None:
                new_score = 0
            i.score = new_score
            i.answers_counter = new_answers_counter
            updated_questions.append(i)
        print('Updating questions\' fields finished. Let\'s apply the changes', time.time() - last_time)
        last_time = time.time()
        Question.objects.bulk_update(updated_questions, ['score', 'answers_counter'], batch_size=100)
        print('Finished applying update of Questions', time.time() - last_time)

        # Profile
        updated = []
        for i in Profile.objects.all():
            new_answers_counter = Answer.objects.filter(author=i).count()
            new_questions_counter = Question.objects.filter(author=i).count()
            answer_likes_sum = AnswerLike.objects.filter(author=i).aggregate(Sum('status')).get('status__sum', 0)
            question_likes_sum = QuestionLike.objects.filter(author=i).aggregate(Sum('status')).get('status__sum', 0)
            i.score = answer_likes_sum + question_likes_sum
            i.answers_counter = new_answers_counter
            i.questions_counter = new_questions_counter
            updated.append(i)

        Profile.objects.bulk_update(updated, ['score', 'answers_counter', 'questions_counter'],
                                    batch_size=100)
        print('Finished applying update of Profiles', time.time() - last_time)

        # Tag
        last_time = time.time()
        updated = []
        for i in Tag.objects.all():
            i.questions_counter = Question.objects.filter(tags__name=i).count()
            updated.append(i)
        Tag.objects.bulk_update(updated, ['questions_counter'], batch_size=100)
        print('Finished applying update of Tags', time.time() - last_time)

        # Answers
        last_time = time.time()
        updated = []
        for i in Answer.objects.all():
            new_score = AnswerLike.objects.filter(answer=i).aggregate(Sum('status')).get('status__sum', 0)
            if new_score is None:
                new_score = 0
            i.score = new_score
            updated.append(i)
        Answer.objects.bulk_update(updated, ['score'], batch_size=100)
        print('Finished applying update of Answers\' likes', time.time() - last_time)

        # Finish
        self.stdout.write(self.style.SUCCESS(f'Successfully added test data with ratio {ratio}.'))
        print('Elapsed time: ', time.time() - script_start_time)
