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