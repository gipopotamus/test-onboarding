import uuid
from typing import Any, Dict, Optional

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .models import Survey, Section, SurveySection, Response
from .utils import consolidate_responses


@method_decorator(csrf_exempt, name='dispatch')
class SurveyView(View):
    """
    Основной класс представления для управления опросами.
    """

    def get(self, request: HttpRequest, survey_id: int, survey_session_id: Optional[str] = None, section_title: str = 'Start') -> JsonResponse:
        """
        Обрабатывает GET-запросы, инициализирует сессию опроса и возвращает соответствующий раздел.

        :param request: HttpRequest объект.
        :param survey_id: ID опроса.
        :param survey_session_id: ID сессии опроса, если уже существует.
        :param section_title: Название текущего раздела.
        :return: HttpResponse с рендерингом страницы или JSON-ответом.
        """
        survey = get_object_or_404(Survey, pk=survey_id)

        if not survey_session_id:
            survey_session_id = str(uuid.uuid4())
            request.session[f"survey_session_{survey_session_id}"] = {
                'survey_id': survey_id,
                'responses': {},
                'current_section': section_title,
                'survey_session_id': survey_session_id
            }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.load_section(request, survey_id, section_title, survey_session_id)

        return render(request, 'app/survey.html', {
            'survey_id': survey_id,
            'survey_session_id': survey_session_id,
            'section_title': section_title
        })

    def load_section(self, request: HttpRequest, survey_id: int, section_title: str, survey_session_id: str) -> JsonResponse:
        """
        Загружает данные текущего раздела опроса для AJAX-запросов.

        :param request: HttpRequest объект.
        :param survey_id: ID опроса.
        :param section_title: Название текущего раздела.
        :param survey_session_id: ID сессии опроса.
        :return: JsonResponse с данными текущего раздела.
        """
        section = get_object_or_404(Section, title=section_title)
        questions = list(section.questions.values('id', 'text', 'type', 'choice_options'))
        session_data = request.session.get(f"survey_session_{survey_session_id}", {})

        return JsonResponse({
            'section': section_title,
            'questions': questions,
            'responses': session_data.get('responses', {}).get(section_title, {})
        })

    def post(self, request: HttpRequest, survey_id: int, section_title: str, survey_session_id: str) -> JsonResponse:
        """
        Обрабатывает POST-запросы, обновляет ответы пользователя и определяет следующий раздел.

        :param request: HttpRequest объект.
        :param survey_id: ID опроса.
        :param section_title: Название текущего раздела.
        :param survey_session_id: ID сессии опроса.
        :return: JsonResponse с информацией о следующем разделе.
        """
        data = request.POST.dict()
        survey = get_object_or_404(Survey, pk=survey_id)
        current_section = get_object_or_404(Section, title=section_title)

        # Проверяем, отвечены ли все обязательные вопросы
        for question in current_section.questions.all():
            question_key = f"question_{question.id}"
            if question.is_required and question_key not in data:
                # Если обязательный вопрос не отвечен, возвращаем ошибку
                return JsonResponse({'error': 'Не все обязательные вопросы были отвечены'}, status=400)

        # Сохраняем ответы в сессии
        session_key = f"survey_session_{survey_session_id}"
        session_data = request.session.get(session_key, {'responses': {}})
        session_data['responses'][section_title] = data
        request.session[session_key] = session_data

        # Определение следующего раздела
        next_section_title = self.determine_next_section(survey, current_section, data)

        if next_section_title == 'Finish':
            # Сохраняем ответы в модель Response при завершении опроса
            final_answers = consolidate_responses(session_data['responses'])
            Response.objects.create(survey=survey, user_id=request.user.id, answers=final_answers)

        return JsonResponse({'next_section': next_section_title})

    def determine_next_section(self, survey: Survey, current_section: Section, data: Dict[str, Any]) -> str:
        """
        Определяет следующий раздел опроса на основе текущего раздела и ответов пользователя.

        :param survey: Объект опроса.
        :param current_section: Текущий раздел.
        :param data: Словарь с данными ответов пользователя.
        :return: Название следующего раздела.
        """
        try:
            survey_section = SurveySection.objects.get(survey=survey, section=current_section)

            if survey_section.has_choice:
                question = current_section.questions.filter(type='choice').first()
                if question:
                    user_choice = data.get(f"question_{question.id}")
                    if user_choice:
                        return Section.objects.get(title=user_choice.strip()).title

            return self.get_next_section_title(survey, current_section)
        except (SurveySection.DoesNotExist, Section.DoesNotExist):
            return 'Finish'

    def get_next_section_title(self, survey: Survey, current_section: Section) -> str:
        """
        Получает название следующего раздела на основе порядка разделов в опросе.

        :param survey: Объект опроса.
        :param current_section: Текущий раздел.
        :return: Название следующего раздела.
        """
        current_survey_section = SurveySection.objects.get(survey=survey, section=current_section)
        next_section = SurveySection.objects.filter(
            survey=survey,
            order__gt=current_survey_section.order
        ).order_by('order').first()

        return next_section.section.title if next_section else 'Finish'
