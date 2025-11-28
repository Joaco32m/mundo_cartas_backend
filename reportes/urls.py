from django.urls import path
from .views import (
    ReporteVentasDiariasAPIView,
    ReporteVentasSemanalesAPIView,
    ReporteVentasMensualesAPIView,
    ReporteExcelAPIView
)

urlpatterns = [
    path("diarias/", ReporteVentasDiariasAPIView.as_view()),
    path("semanales/", ReporteVentasSemanalesAPIView.as_view()),
    path("mensuales/", ReporteVentasMensualesAPIView.as_view()),
    path("excel/", ReporteExcelAPIView.as_view()),
]
