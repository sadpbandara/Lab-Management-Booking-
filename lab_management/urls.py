from django.contrib import admin
from django.urls import path
from bookings.views import home_view
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', home_view, name='home'), # මුල් පිටුව සඳහා
    path('bookings/', include('bookings.urls')),
]