"""
Root URL configuration for VoiceTasks.

Routes:
  /               → core (dashboard)
  /tasks/         → tasks app
  /voice/         → voice app
  /analysis/      → analysis app
  /settings/      → settings_ui app
  /providers/     → providers app
  /admin/         → Django admin
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('voice/', include('apps.voice.urls')),
    path('analysis/', include('apps.analysis.urls')),
    path('settings/', include('apps.settings_ui.urls')),
    path('providers/', include('apps.providers.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
