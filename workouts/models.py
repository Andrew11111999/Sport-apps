from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class WorkoutPlan(models.Model):
    WORKOUT_TYPES = [
        ('home_strength', '💪 Домашняя сила'),
        ('home_cardio', '🏃 Домашнее кардио'),
        ('gym_strength', '🏋️ Силовая в зале'),
        ('gym_cardio', '🚴 Кардио в зале'),
        ('yoga', '🧘 Йога и растяжка'),
    ]

    DIFFICULTY_LEVELS = [
        ('beginner', '🟢 Начинающий'),
        ('intermediate', '🟡 Средний'),
        ('advanced', '🔴 Продвинутый'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    name = models.CharField(max_length=200)
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    description = models.TextField()
    duration = models.IntegerField(help_text="Длительность в минутах")
    calories_burned = models.IntegerField(default=0)
    image = models.ImageField(upload_to='workouts/', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['workout_type', 'difficulty']),
            models.Index(fields=['is_public', 'created_at']),
        ]
        ordering = ['-created_at']

    def str(self):
        return f"{self.name} ({self.get_workout_type_display()})"


class Exercise(models.Model):
    EQUIPMENT_CHOICES = [
        ('none', 'Без оборудования'),
        ('dumbbells', 'Гантели'),
        ('barbell', 'Штанга'),
        ('resistance_bands', 'Эспандеры'),
        ('yoga_mat', 'Коврик'),
        ('machine', 'Тренажер'),
    ]

    workout = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100)
    description = models.TextField()
    sets = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    reps = models.CharField(max_length=50, help_text="Например: 10-12 или 30 секунд")
    rest_time = models.IntegerField(help_text="Отдых в секундах", default=60)
    equipment = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES, default='none')
    demonstration_url = models.URLField(blank=True, help_text="Ссылка на видео демонстрацию")
    order = models.IntegerField(default=0)
    target_muscles = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['workout', 'order']

    def str(self):
        return self.name


class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    completed_exercises = models.IntegerField(default=0)
    total_sets = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )

    @property
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).seconds // 60
        return 0

    @property
    def efficiency(self):
        if self.duration > 0:
            return (self.completed_exercises / self.duration) * 100
        return 0

    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]
        ordering = ['-start_time']


class ExerciseLog(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercise_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    completed_sets = models.IntegerField(default=0)
    completed_reps = models.JSONField(default=dict)  # Хранение повторений по подходам
    weight_used = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['session', 'exercise']),
        ]
