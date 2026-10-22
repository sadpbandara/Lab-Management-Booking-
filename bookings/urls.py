from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('book-laptop/', views.book_laptop_view, name='book_laptop'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('export/bookings/', views.export_bookings_excel, name='export_bookings'),
    path('mark-attendance/<int:booking_id>/', views.mark_attendance_view, name='mark_attendance'),
    path('reports/students/', views.student_report_view, name='student_report'),
    path('holidays/', views.manage_holidays_view, name='manage_holidays'),
    path('holidays/edit/<int:event_id>/', views.edit_holiday_view, name='edit_holiday'),
    path('holidays/delete/<int:event_id>/', views.delete_holiday_view, name='delete_holiday'),
    
]