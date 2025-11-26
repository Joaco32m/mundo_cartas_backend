from django.urls import path
from . import views

urlpatterns = [
    path('', views.CarritoDetail.as_view(), name='api_carrito_detail'),               
    path('add/', views.AgregarAlCarrito.as_view(), name='api_carrito_add'),          
    path('item/<int:item_id>/increment/', views.ModificarItem.as_view(), {'action': 'increment'}, name='api_item_increment'),
    path('item/<int:item_id>/decrement/', views.ModificarItem.as_view(), {'action': 'decrement'}, name='api_item_decrement'),
    path('item/<int:item_id>/', views.EliminarItem.as_view(), name='api_item_delete'),
    path('checkout/', views.Checkout.as_view(), name='api_carrito_checkout'),
]