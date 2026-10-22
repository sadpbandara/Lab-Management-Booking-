from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # පරිශීලකයා කවුරුන්ද යන්න හඳුනාගැනීමට
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Batch(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    name = models.CharField(max_length=50, unique=True)
    # එක් එක් කණ්ඩායමට වෙන් කළ විශේෂ දිනය (Dedicated Day)
    dedicated_day = models.IntegerField(choices=DAYS_OF_WEEK) 

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    reg_no = models.CharField(max_length=50, unique=True)
    e_number = models.CharField(max_length=50, unique=True)
    programme = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name='students')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.reg_no}"

class LecturerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='lecturer_profile')
    # කථිකාචාර්යවරුන්ට අදාළ අමතර තොරතුරු මෙහි ඇතුළත් කළ හැක
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()