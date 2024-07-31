from django.urls import path

from ecomadmin.views import *

app_name = 'dashboard'
urlpatterns = [
    path('', AdminView.as_view(), name="admin_index"),

    # category CRD (Create, Read, Delete)
    path('insert/category', CategoryFormView.as_view(), name="category_form"),
    path('category', CategoryView.as_view(), name="category"),
    path('delete/category/<slug:slug>/', CategoryDeleteView.as_view(), name='delete_category'),

    # product RD (Read, Delete)
    path('product', ProductView.as_view(), name="product"),
    path('delete/product/<slug:slug>/', ProductDeleteView.as_view(), name='delete_product'),

    # # vendor RUD (Read, Update, Delete)
    path('vendor', VendorView.as_view(), name="vendor"),
    path('update/vendor/<int:pk>', VendorUpdateFormView.as_view(), name="vendor_update_form"),
    path('delete/vendor/<int:pk>/', VendorDeleteView.as_view(), name='delete_vendor'),

    # # vendor R (Read)
    path('customer', CustomerView.as_view(), name="customer"),

    # order RUD (Read, Update, Delete)
    path('order', OrderView.as_view(), name="order"),
    path('update/order/<int:pk>', OrderUpdateFormView.as_view(), name="order_update_form"),
    # path('delete/order/<slug:slug>/', OrderDeleteView.as_view(), name='delete_order'),

    # # tracking RUD (Read, Update, Delete)
    path('tracking', TrackingView.as_view(), name="tracking"),
    path('update/tracking/<int:pk>', TrackingUpdateFormView.as_view(), name="tracking_update_form"),
    # path('delete/tracking/<slug:slug>/', TrackingDeleteView.as_view(), name='delete_tracking'),

    # # transaction RD (Read, Delete)
    path('transaction', TransactionView.as_view(), name="transaction"),

    # banner CRD (Create, Read, Delete)
    path('insert/banner', BannerFormView.as_view(), name="banner_form"),
    path('banner', BannerView.as_view(), name="banner"),
    path('delete/banner/<int:pk>/', BannerDeleteView.as_view(), name='delete_banner'),

    # about CRU (Create, Read, Update)
    path('insert/about-us', AboutUsFormView.as_view(), name="about_us_form"),
    path('about-us/', AboutUsView.as_view(), name="about_us"),
    path('update/about-us/<int:pk>/', AboutUsUpdateFormView.as_view(), name='about_us_update_form'),
]
