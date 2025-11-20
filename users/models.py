from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', '📉 Похудение'),
        ('muscle_gain', '💪 Набор мышечной массы'),
        ('endurance', '🏃 Выносливость'),
        ('general_fitness', '🌟 Общая физическая форма'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    height = models.FloatField(help_text="Рост в см", null=True, blank=True)
    weight = models.FloatField(help_text="Вес в кг", null=True, blank=True)
    fitness_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general_fitness')
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый')
    ], default='beginner')
    daily_calorie_target = models.IntegerField(default=2000)
    protein_target = models.IntegerField(default=150, help_text="Грамм в день")

    def str(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()