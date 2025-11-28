from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
from .models import WorkoutSession, Exercise, ExerciseLog


@csrf_exempt
@require_POST
@login_required
def save_exercise_progress(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        exercise_id = data.get('exercise_id')
        completed_sets = data.get('completed_sets', 0)
        weight_used = data.get('weight_used')

        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        exercise = get_object_or_404(Exercise, id=exercise_id)

        # Создаем или обновляем лог упражнения
        log, created = ExerciseLog.objects.get_or_create(
            session=session,
            exercise=exercise,
            defaults={
                'completed_sets': completed_sets,
                'weight_used': weight_used,
            }
        )

        if not created:
            log.completed_sets = completed_sets
            log.weight_used = weight_used
            log.save()

        return JsonResponse({'status': 'success', 'log_id': log.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def progress_dashboard(request):
    # Статистика пользователя
    user_sessions = WorkoutSession.objects.filter(user=request.user)

    total_sessions = user_sessions.count()
    total_minutes = user_sessions.aggregate(
        total=Sum('duration')
    )['total'] or 0

    # Последние 5 тренировок
    recent_sessions = user_sessions[:5]

    # Статистика по типам тренировок
    workout_stats = WorkoutSession.objects.filter(
        user=request.user
    ).values(
        'workout_plan__workout_type'
    ).annotate(
        count=Count('id'),
        total_duration=Sum('duration')
    )

    context = {
        'total_sessions': total_sessions,
        'total_minutes': total_minutes,
        'recent_sessions': recent_sessions,
        'workout_stats': workout_stats,
    }
    return render(request, 'workouts/progress_dashboard.html', context)