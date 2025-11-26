from django.urls import path
from . import views

urlpatterns = [
    path('', views.CarritoDetail.as_view()),
    path('add/', views.AgregarAlCarrito.as_view()),
    path('item/<int:item_id>/increment/', views.ModificarItem.as_view(), {'action': 'increment'}),
    path('item/<int:item_id>/decrement/', views.ModificarItem.as_view(), {'action': 'decrement'}),
    path('item/<int:item_id>/', views.EliminarItem.as_view()),
    
    # Nuevo
    path('checkout/cliente/', views.CheckoutCliente.as_view()),
    path('checkout/vendedor/', views.CheckoutVendedor.as_view()),
]
