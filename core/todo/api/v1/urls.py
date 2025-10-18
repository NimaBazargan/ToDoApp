from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = "api-v1"

router = DefaultRouter()
router.register("task", views.TaskModelViewSet, basename="task")

urlpatterns = [
    path("weather/", views.WeatherApiView.as_view(), name="weather")
] + router.urls
