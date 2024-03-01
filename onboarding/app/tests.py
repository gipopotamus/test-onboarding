from django.test import TestCase
from .models import Survey, Section, Question


class SurveyCreationTest(TestCase):
    def setUp(self):
        # Создаем опрос
        self.survey = Survey.objects.create(
            title="Тестовый опрос",
            description="Описание тестового опроса"
        )

        # Создаем секции
        self.section1 = Section.objects.create(title="Секция 1")
        self.section2 = Section.objects.create(title="Секция 2")

        # Создаем вопросы
        self.question1 = Question.objects.create(
            section=self.section1,
            text="Первый вопрос",
            type="text"
        )

        self.question2 = Question.objects.create(
            section=self.section1,
            text="Второй вопрос",
            type="choice",
            choice_options="Опция 1, Опция 2, Опция 3"
        )

        self.question3 = Question.objects.create(
            section=self.section2,
            text="Третий вопрос",
            type="text"
        )

    def test_survey_creation(self):
        # Проверяем, что опрос и все его элементы были успешно созданы
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(Section.objects.count(), 2)
        self.assertEqual(Question.objects.count(), 3)

        # Проверяем, что вопросы принадлежат правильным секциям
        self.assertEqual(self.section1.questions.count(), 2)
        self.assertEqual(self.section2.questions.count(), 1)

        # Проверяем содержимое вопросов
        self.assertEqual(self.question1.text, "Первый вопрос")
        self.assertEqual(self.question2.type, "choice")
        self.assertIn("Опция 1", self.question2.choice_options)
        self.assertEqual(self.question3.section, self.section2)
