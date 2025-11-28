from django.urls import path
from . import views

urlpatterns = [
    path('', views.workout_list, name='workout_list'),
    path('workout/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('workout/<int:pk>/start/', views.start_workout, name='start_workout'),
    path('workout/session/<int:session_id>/', views.workout_session, name='workout_session'),
    path('workout/session/<int:session_id>/complete/', views.complete_workout, name='complete_workout'),
    path('progress/', views.progress_dashboard, name='progress_dashboard'),
    path('api/save-exercise/', views.save_exercise_progress, name='save_exercise_progress'),
]