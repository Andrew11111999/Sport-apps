from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('workouts.urls')),
    path('users/', include('users.urls')),
    path('nutrition/', include('nutrition.urls')),
    path('manifest.json', TemplateView.as_view(
        template_name='manifest.json',
        content_type='application/json',
    ), name='manifest'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
