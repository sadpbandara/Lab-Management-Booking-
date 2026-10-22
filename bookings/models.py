from django.db import models
from accounts.models import StudentProfile, LecturerProfile

class Laptop(models.Model):
    lap_no = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"Laptop {self.lap_no}"

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

class SpecialEvent(models.Model):
    EVENT_TYPES = [
        ('holiday', 'Holiday'),
        ('exam_it', 'IT Exam'),
        ('exam_english', 'English Exam'),
        ('other', 'Other Blocked Event'),
    ]
    date = models.DateField(unique=True) # මෙම දිනවල ළමුන්ට වෙන්කිරීම් කළ නොහැක
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.date}"

class Booking(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='bookings')
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    
    # එක් සැසියකට කථිකාචාර්යවරුන් කිහිපදෙනෙකු අනුයුක්ත කිරීමට
    assigned_lecturers = models.ManyToManyField(LecturerProfile, related_name='assigned_sessions')
    
    attendance = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # එකම දවසේ, එකම වේලාවට, එකම ලැප්ටොප් එක දෙදෙනෙකුට වෙන් කිරීම මෙමගින් වළක්වයි
        unique_together = ('laptop', 'date', 'time_slot')

    def __str__(self):
        return f"{self.student.reg_no} - {self.laptop.lap_no} on {self.date}"