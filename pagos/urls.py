from django.urls import path
from . import views

urlpatterns = [
    path("webpay/init/", views.iniciar_pago),
    path("webpay/confirm/", views.confirmar_pago),
]