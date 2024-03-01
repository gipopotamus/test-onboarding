from django.urls import path
from .views import SurveyView

urlpatterns = [
    # URL для начала опроса и загрузки первой секции
    path('survey/<int:survey_id>/', SurveyView.as_view(), name='start_survey'),

    # URL для загрузки конкретной секции и отправки ответов
    path('survey/<int:survey_id>/<uuid:survey_session_id>/<str:section_title>/', SurveyView.as_view(), name='survey_section'),
]
