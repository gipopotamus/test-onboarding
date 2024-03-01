from django.core.exceptions import ValidationError
from django.db import models
import uuid


class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class Section(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Question(models.Model):
    SECTION_TYPES = (
        ('text', 'Text'),
        ('choice', 'Choice'),
    )

    section = models.ForeignKey(Section, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=1024, blank=True, null=True)  # Текст вопроса
    type = models.CharField(max_length=50, choices=SECTION_TYPES, default='text')
    choice_options = models.TextField(blank=True, null=True)  # Текстовое поле для хранения вариантов выбора, разделенных запятой
    is_required = models.BooleanField(default=False, verbose_name="Обязательный вопрос")

    def __str__(self):
        return self.text or "Choice question"

    def save(self, *args, **kwargs):
        if self.type == 'choice' and not self.choice_options:
            raise ValidationError("Для вопросов с выбором должны быть указаны варианты.")
        if self.type == 'text' and self.choice_options:
            raise ValidationError("Для текстовых вопросов не должно быть вариантов выбора.")
        super().save(*args, **kwargs)

    def get_choices(self):
        """ Возвращает список вариантов ответа для вопроса с выбором. """
        return self.choice_options.split(',') if self.choice_options else []


class SurveySection(models.Model):
    survey = models.ForeignKey(Survey, related_name='sections', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    has_choice = models.BooleanField(default=False)  # Указывает, является ли следующая секция динамической

    class Meta:
        ordering = ['order']
        unique_together = ('survey', 'section', 'order')

    def __str__(self):
        has_choice = "(next dynamic)" if self.has_choice else ""
        return f"{self.survey.title} - {self.order}: {self.section.title} {has_choice}"


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255)
    answers = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.survey} - {self.user_id}"
