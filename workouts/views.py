from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
import json
from .models import WorkoutPlan, Exercise, WorkoutSession, ExerciseLog


def workout_list(request):
    workout_type = request.GET.get('type', '')
    difficulty = request.GET.get('difficulty', '')
    equipment = request.GET.get('equipment', '')

    workouts = WorkoutPlan.objects.filter(is_public=True)

    if workout_type:
        workouts = workouts.filter(workout_type=workout_type)
    if difficulty:
        workouts = workouts.filter(difficulty=difficulty)
    if equipment:
        workouts = workouts.filter(exercises__equipment=equipment).distinct()

    # Статистика для фильтров
    workout_stats = {
        'total_workouts': workouts.count(),
        'home_workouts': workouts.filter(workout_type__startswith='home').count(),
        'gym_workouts': workouts.filter(workout_type__startswith='gym').count(),
    }

    context = {
        'workouts': workouts,
        'workout_stats': workout_stats,
        'current_filters': {
            'type': workout_type,
            'difficulty': difficulty,
            'equipment': equipment,
        }
    }
    return render(request, 'workouts/workout_list.html', context)


@login_required
def workout_detail(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)
    exercises = workout.exercises.all()

    # Проверяем, завершал ли пользователь эту тренировку
    user_completions = WorkoutSession.objects.filter(
        user=request.user,
        workout_plan=workout
    ).count()

    context = {
        'workout': workout,
        'exercises': exercises,
        'user_completions': user_completions,
        'exercises_json': json.dumps([
            {
                'id': ex.id,
                'name': ex.name,
                'sets': ex.sets,
                'reps': ex.reps,
                'rest_time': ex.rest_time,
                'description': ex.description,
            }
            for ex in exercises
        ])
    }
    return render(request, 'workouts/workout_detail.html', context)


@login_required
def start_workout(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)

    # Создаем сессию тренировки
    session = WorkoutSession.objects.create(
        user=request.user,
        workout_plan=workout,
        start_time=timezone.now()
    )

    return redirect('workout_session', session_id=session.id)


@login_required
def workout_session(request, session_id):
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    workout = session.workout_plan
    exercises = workout.exercises.all()

    context = {
        'session': session,
        'workout': workout,
        'exercises': exercises,
        'exercises_json': json.dumps([
            {
                'id': ex.id,
                'name': ex.name,
                'sets': ex.sets,
                'reps': ex.reps,
                'rest_time': ex.rest_time,
                'description': ex.description,
            }
            for ex in exercises
        ])
    }
    return render(request, 'workouts/workout_session.html', context)


@login_required
def progress_dashboard(request):
    # Базовая статистика
    user_sessions = WorkoutSession.objects.filter(user=request.user)

    total_stats = user_sessions.aggregate(
        total_sessions=Count('id'),
        total_minutes=Sum('duration'),
        avg_rating=Avg('rating'),
        total_calories=Sum('workout_plan__calories_burned')
    )

    # Статистика за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_stats = user_sessions.filter(
        start_time__gte=thirty_days_ago
    ).aggregate(
        sessions=Count('id'),
        minutes=Sum('duration'),
        avg_duration=Avg('duration')
    )

    # Распределение по типам тренировок
    workout_distribution = user_sessions.values(
        'workout_plan__workout_type'
    ).annotate(
        count=Count('id'),
        total_duration=Sum('duration')
    ).order_by('-count')

    # Последние тренировки
    recent_sessions = user_sessions.select_related('workout_plan')[:10]

    # Прогресс по неделям
    weekly_progress = user_sessions.extra({
        'week': "EXTRACT(WEEK FROM start_time)",
        'year': "EXTRACT(YEAR FROM start_time)"
    }).values('year', 'week').annotate(
        sessions=Count('id'),
        total_minutes=Sum('duration')
    ).order_by('-year', '-week')[:8]

    context = {
        'total_stats': total_stats,
        'monthly_stats': monthly_stats,
        'workout_distribution': workout_distribution,
        'recent_sessions': recent_sessions,
        'weekly_progress': weekly_progress,
    }
    return render(request, 'workouts/progress_dashboard.html', context)
