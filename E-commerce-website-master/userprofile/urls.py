
from django.urls import path


from . import views

urlpatterns = [
    path('seller/', views.seller, name='seller'),
    path('seller/order-detail/<int:pk>/', views.seller_order_detail, name='seller_order_detail'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('seller/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('seller/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
]