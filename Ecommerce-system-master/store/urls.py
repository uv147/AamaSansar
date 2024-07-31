from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import ProductListView, AddProfileView, ProfileView, UpdateProfileView, ResetPasswordView, \
    ChangePasswordView, verify_payment

urlpatterns = [
    path('login', views.handlelogin, name='login'),
    path('signup', views.handlesignup, name='signup'),
    path('otp-verify', views.otp_verify, name='otp verification'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),

    path("logout/", LogoutView.as_view(), name="logout"),
    path('search', views.search, name='search'),
    path('add-to-cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('change-quantity/<str:product_id>', views.change_quantity, name='change_quantity'),
    path('remove-from-cart/<str:product_id>', views.remove_from_cart, name='remove_from_cart'),
    path('cart', views.cart_view, name='cart_view'),
    path('<int:pk>/cart/checkout', views.checkout, name='checkout'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product', ProductListView.as_view(), name='product_list'),
    path('add-profile/<int:pk>', AddProfileView.as_view(), name='add_profile'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('update-profile/<str:username>/<int:pk>', UpdateProfileView.as_view(), name='update_profile'),

    path('api/verify_payment',verify_payment,name='verify_payment'),


]
