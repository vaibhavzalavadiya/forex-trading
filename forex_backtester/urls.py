from django.contrib import admin
from django.urls import path, include  # ✅ include added here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backtester.urls')),  # ✅ include your app's urls
]
