from typing import Dict, Any
from .models import Question


def consolidate_responses(responses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Преобразует ответы из различных секций в один JSON объект,
    заменяя ключи вида 'question_{id}' на текст вопроса.

    :param responses: Ответы пользователя, разделенные по секциям.
    :return: Одиночный JSON объект с ответами.
    """
    consolidated_responses = {}
    for section, answers in responses.items():
        for key, value in answers.items():
            question_id = key.split('_')[-1]
            try:
                question = Question.objects.get(pk=question_id)
                question_text = question.text
                consolidated_responses[question_text] = value
            except Question.DoesNotExist:
                continue
    return consolidated_responses
