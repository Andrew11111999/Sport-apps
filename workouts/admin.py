from django.contrib import admin
from .models import WorkoutPlan, Exercise, WorkoutSession, ExerciseLog

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout_type', 'difficulty', 'duration', 'is_public', 'created_at']
    list_filter = ['workout_type', 'difficulty', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_public']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout', 'sets', 'reps', 'equipment']
    list_filter = ['equipment', 'workout__workout_type']
    search_fields = ['name', 'target_muscles']

class ExerciseLogInline(admin.TabularInline):
    model = ExerciseLog
    extra = 0

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_plan', 'start_time', 'duration', 'rating']
    list_filter = ['start_time', 'rating']
    inlines = [ExerciseLogInline]
