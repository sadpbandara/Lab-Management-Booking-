from django.contrib import admin
from .models import Laptop, TimeSlot, SpecialEvent, Booking

admin.site.register(Laptop)
admin.site.register(TimeSlot)
admin.site.register(SpecialEvent)
admin.site.register(Booking)