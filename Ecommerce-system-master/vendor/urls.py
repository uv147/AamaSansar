from django.urls import path

from . import views
from .views import SellerProfileView, SellerProfileUpdateView

# app_name = 'vendor'

urlpatterns = [
    # path('seller-login', views.handlesellerlogin, name='handlesellerlogin'),
    path('vendor-signup', views.handlesellersignup, name='handlesellersignup'),
    path('<int:pk>/', views.seller, name='seller'),
    path('<int:pk>/add-profile', SellerProfileView.as_view(), name="seller_profile"),
    path('<int:user_pk>/order-detail/<int:order_pk>/', views.seller_order_detail, name='seller_order_detail'),
    path('<int:pk>/add-product/', views.add_product, name='add_product'),
    path('<int:user_pk>/edit-product/<int:product_pk>/', views.edit_product, name='edit_product'),
    path('<int:user_pk>/delete-product/<int:product_pk>/', views.delete_product, name='delete_product'),
    path('<int:pk>/profile', views.vendor_detail, name='vendor_detail'),
    path('<int:upk>/update-profile/<int:pk>', SellerProfileUpdateView.as_view(), name="seller_profile_update"),

]
