from django.urls import path
from .views import RegistroAPIView, user_profile

urlpatterns = [
    path('registro/', RegistroAPIView.as_view(), name='registro_api'),
    path('perfil/', user_profile, name='user_profile'),
]

