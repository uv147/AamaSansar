from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from core.views import frontpage

urlpatterns = [
    # path('ecomadmin/', ecomadmin.site.urls),
    path('admin/', include('ecomadmin.urls')),
    path('vendor/', include('vendor.urls')),
    path('',include('store.urls')),
    path('',frontpage,name='frontpage'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  