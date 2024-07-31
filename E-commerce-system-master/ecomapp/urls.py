from django.urls import path
from .views import *

app_name ="ecomapp"
urlpatterns = [
    path("",HomeView.as_view(), name="home"),
    path("login/",LoginView.as_view(), name="login"),
    path("register/",RegisterView.as_view(), name="register"),
    path("seller/",SellerView.as_view(), name="seller"),
    path("product/<slug:slug>/",ProductDetailView.as_view(),name="productdetail"),
    path("add-to-cart-<int:pro_id>/",AddToCartView.as_view(),name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    


   

]