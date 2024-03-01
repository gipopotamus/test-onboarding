from django.contrib import admin
from .models import Survey, Section, Question, SurveySection, Response


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Количество дополнительных форм для создания новых вопросов
    fields = ['text', 'type', 'choice_options', 'is_required']


class SurveySectionInline(admin.TabularInline):
    model = SurveySection
    extra = 1  # Количество дополнительных форм для создания новых секций
    fields = ['section', 'order', 'has_choice']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    inlines = [SurveySectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'section', 'type', 'choice_options', 'is_required']
    list_filter = ['section', 'type', 'is_required']
    fields = ['section', 'text', 'type', 'choice_options', 'is_required']


@admin.register(SurveySection)
class SurveySectionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'section', 'order', 'has_choice']
    list_filter = ['survey', 'section']
    list_editable = ['order', 'has_choice']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'user_id', 'id']
    readonly_fields = ['answers']
    fields = ['survey', 'user_id', 'answers']
    list_filter = ['survey']
