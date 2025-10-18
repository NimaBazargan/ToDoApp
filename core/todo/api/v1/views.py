from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from .serializers import TaskSerializer, WeatherSerializer
from todo.models import Task
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import TaskFilter
from .paginations import DefaultPagination
from rest_framework.views import APIView
import requests
from persiantools.jdatetime import JalaliDateTime
import pytz
from rest_framework.response import Response
from django.core.cache import cache


class TaskModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "user__user__email"]
    ordering_fields = ["created_date", "user"]
    pagination_class = DefaultPagination
    filterset_class = TaskFilter


class WeatherApiView(APIView):
    serializer_class = WeatherSerializer
    KEY = 'Your_Key'

    def find_latlon(self, city_name):
        """
        :return: lat and lon of the city
        """
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={self.KEY}&units=metric"
            response = requests.get(url)
            response_json = response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Somthing Else", err)
        else:
            return response_json[0]["lat"], response_json[0]["lon"]

    def post(self, request):
        """

        :return: weather data
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        city_name = serializer.validated_data["city"]
        cache_key = f"weather_data_{city_name}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({"data": cached_data})
        lat, lon = self.find_latlon(city_name)
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Somthing Else", err)
        response = response.json()
        data = {
            "main": response["weather"][0]["main"],
            "description": response["weather"][0]["description"],
            "main_temp": response["main"]["temp"],
            "main_feels_like": response["main"]["feels_like"],
            "main_humidity": response["main"]["humidity"],
            "main_temp_min": response["main"]["temp_min"],
            "main_temp_max": response["main"]["temp_max"],
            "visibility": response["visibility"],
            "wind_speed": response["wind"]["speed"],
            "sys_sunrise": JalaliDateTime.fromtimestamp(
                response["sys"]["sunrise"], pytz.timezone("Asia/Tehran")
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "sys_sunset": JalaliDateTime.fromtimestamp(
                response["sys"]["sunset"], pytz.timezone("Asia/Tehran")
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }
        cache.set(cache_key, data, 1200)
        return Response(data)
