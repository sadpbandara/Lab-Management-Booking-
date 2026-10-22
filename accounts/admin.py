from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Batch, StudentProfile, LecturerProfile

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Batch)
admin.site.register(StudentProfile)
admin.site.register(LecturerProfile)