from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.student_signup_view, name='student_signup'),
    path('pending-approvals/', views.pending_students_view, name='pending_students'),
    path('upload-students/', views.upload_students_csv, name='upload_students'),
    path('edit-student/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('batches/', views.manage_batches_view, name='manage_batches'),
    path('batches/edit/<int:batch_id>/', views.edit_batch_view, name='edit_batch'),
    path('batches/delete/<int:batch_id>/', views.delete_batch_view, name='delete_batch'),
]