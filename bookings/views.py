import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Laptop, TimeSlot, SpecialEvent, Booking
from accounts.models import StudentProfile

from django.shortcuts import get_object_or_404

import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from accounts.models import StudentProfile # Report එකට සිසුන්ගේ ලැයිස්තුව ගැනීමට

from django.shortcuts import render, redirect # redirect යන්න import කර ඇති බව තහවුරු කරගන්න

def home_view(request):
    # පරිශීලකයා දැනටමත් ලොග් වී සිටී නම්
    if request.user.is_authenticated:
        # Admin හෝ Lecturer කෙනෙකු නම් කෙලින්ම Lecturer Dashboard එකට යවන්න
        if request.user.is_superuser or request.user.is_lecturer:
            return redirect('lecturer_dashboard')
        # සිසුවෙකු නම් කෙලින්ම Student Dashboard එකට යවන්න
        elif request.user.is_student:
            return redirect('student_dashboard')
            
    # ලොග් වී නොමැති අයට පමණක් මුල් පිටුව (Login/Signup පෙන්වන පිටුව) පෙන්වන්න
    return render(request, 'home.html')

@login_required(login_url='/accounts/login/')
def student_dashboard(request):
    try:
        # ලොග් වී සිටින සිසුවාගේ වෙන්කිරීම් ලබාගැනීම
        student_profile = request.user.student_profile
        my_bookings = Booking.objects.filter(student=student_profile).order_by('-date', '-time_slot__start_time')
    except:
        # Student profile එකක් නොමැති නම්
        my_bookings = None
        
    context = {
        'my_bookings': my_bookings
    }
    return render(request, 'student_dashboard.html', context)

@login_required(login_url='/accounts/login/')
def book_laptop_view(request):
    laptops = Laptop.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    today = timezone.now().date()

    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        time_slot_id = request.POST.get('time_slot')
        laptop_id = request.POST.get('laptop')

        # 1. තෝරාගත් දිනය නිවාඩු දිනයක් හෝ විභාග දිනයක්දැයි බැලීම (SpecialEvent check)
        is_blocked = SpecialEvent.objects.filter(date=booking_date).exists()
        if is_blocked:
            messages.error(request, "සමාවෙන්න! මෙම දිනයේ විභාගයක් හෝ විශේෂ නිවාඩුවක් ඇති බැවින් වෙන්කිරීම් කළ නොහැක.")
            return redirect('book_laptop')

        # 2. අදාළ ලැප්ටොප් එක එම වේලාවට වෙනත් අයෙකු වෙන්කර ඇත්දැයි බැලීම
        is_booked = Booking.objects.filter(date=booking_date, time_slot_id=time_slot_id, laptop_id=laptop_id).exists()
        if is_booked:
            messages.error(request, "මෙම ලැප්ටොප් යන්ත්‍රය අදාළ වේලාව සඳහා දැනටමත් වෙනත් සිසුවෙකු වෙන්කර ඇත. කරුණාකර වෙනත් එකක් තෝරන්න.")
            return redirect('book_laptop')

        # 3. වෙන්කිරීම සාර්ථකව Database එකට ඇතුළත් කිරීම
        try:
            # පරිශීලකයාට අදාළ StudentProfile එක ලබා ගැනීම
            # (දැනට Admin කෙනෙකු ලොග් වී StudentProfile එකක් නොමැති නම් Error එකක් නොපැමිණීමට මෙය try-except තුළ දමා ඇත)
            student_profile = request.user.student_profile
            
            Booking.objects.create(
                student=student_profile,
                laptop_id=laptop_id,
                date=booking_date,
                time_slot_id=time_slot_id
            )
            messages.success(request, "ඔබගේ වෙන්කිරීම සාර්ථකයි!")
            return redirect('student_dashboard')
            
        except request.user._meta.model.student_profile.RelatedObjectDoesNotExist:
            messages.error(request, "ඔබ Student ගිණුමකින් ලොග් වී නොමැත. වෙන්කිරීම් කළ හැක්කේ සිසුන්ට පමණි.")
            return redirect('book_laptop')

    context = {
        'laptops': laptops,
        'time_slots': time_slots,
        'today': today
    }
    return render(request, 'book_laptop.html', context)

# Lecturer Dashboard View
@login_required(login_url='/accounts/login/')
def lecturer_dashboard(request):
    # සියලුම වෙන්කිරීම් ලබාගැනීම
    all_bookings = Booking.objects.all().order_by('-date', '-time_slot__start_time')
    
    context = {
        'all_bookings': all_bookings
    }
    return render(request, 'lecturer_dashboard.html', context)

# Excel (CSV) Download View
@login_required(login_url='/accounts/login/')
def export_bookings_excel(request):
    response = HttpResponse(content_type='text/csv')
    # බාගත වන ගොනුවේ නම
    response['Content-Disposition'] = 'attachment; filename="Lab_Bookings_List.csv"'
    
    writer = csv.writer(response)
    # Excel ගොනුවේ මාතෘකා (Headers)
    writer.writerow(['Booked Date', 'Time Slot', 'Laptop No', 'Student Reg No', 'Attendance', 'Remark'])
    
    bookings = Booking.objects.all().order_by('-date', '-time_slot__start_time')
    
    # දත්ත එකින් එක ගොනුවට ලිවීම
    for booking in bookings:
        time_str = f"{booking.time_slot.start_time.strftime('%I:%M %p')} - {booking.time_slot.end_time.strftime('%I:%M %p')}"
        attendance_status = "Yes" if booking.attendance else "No"
        
        writer.writerow([
            booking.date,
            time_str,
            booking.laptop.lap_no,
            booking.student.reg_no,
            attendance_status,
            booking.remark
        ])
        
    return response

@login_required(login_url='/accounts/login/')
def mark_attendance_view(request, booking_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        # දැනට ඇති තත්ත්වය අනිත් පැත්තට හැරවීම (Toggle)
        booking.attendance = not booking.attendance
        booking.save()
        
    return redirect('lecturer_dashboard')

@login_required(login_url='/accounts/login/')
def student_dashboard(request):
    try:
        student_profile = request.user.student_profile
        my_bookings = Booking.objects.filter(student=student_profile).order_by('-date', '-time_slot__start_time')
        
        # පැමිණි මුළු පැය ගණනය කිරීම
        attended_bookings = my_bookings.filter(attendance=True)
        total_seconds = 0
        for b in attended_bookings:
            dt_start = datetime.combine(date.today(), b.time_slot.start_time)
            dt_end = datetime.combine(date.today(), b.time_slot.end_time)
            total_seconds += (dt_end - dt_start).total_seconds()
            
        total_hours = round(total_seconds / 3600, 2) # තත්පර පැය බවට පත් කිරීම
        
    except:
        my_bookings = None
        total_hours = 0
        
    context = {
        'my_bookings': my_bookings,
        'total_hours': total_hours # මෙය template එකට යවමු
    }
    return render(request, 'student_dashboard.html', context)

# 2. Admin/Lecturer සඳහා අලුත් Report View එක
@login_required(login_url='/accounts/login/')
def student_report_view(request):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    students = StudentProfile.objects.filter(is_approved=True)
    selected_student = None
    report_bookings = None
    total_hours = 0
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    student_id = request.GET.get('student_id')

    if student_id:
        selected_student = get_object_or_404(StudentProfile, id=student_id)
        # මූලිකවම අදාළ සිසුවා පැමිණි සියලුම වෙන්කිරීම් ලබාගැනීම
        report_bookings = Booking.objects.filter(student=selected_student, attendance=True).order_by('date')
        
        # දින පරාසයක් ලබා දී ඇත්නම් ඒ අනුව Filter කිරීම
        if start_date:
            report_bookings = report_bookings.filter(date__gte=start_date)
        if end_date:
            report_bookings = report_bookings.filter(date__lte=end_date)
            
        # අදාළ කාලයට පැය ගණනය කිරීම
        total_seconds = 0
        for b in report_bookings:
            dt_start = datetime.combine(date.today(), b.time_slot.start_time)
            dt_end = datetime.combine(date.today(), b.time_slot.end_time)
            total_seconds += (dt_end - dt_start).total_seconds()
        total_hours = round(total_seconds / 3600, 2)

    context = {
        'students': students,
        'selected_student': selected_student,
        'report_bookings': report_bookings,
        'total_hours': total_hours,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'student_report.html', context)

# bookings/views.py (යාවත්කාලීන කළ යුතු කොටස)

@login_required(login_url='/accounts/login/')
def lecturer_dashboard(request):
    filter_date = request.GET.get('filter_date')
    
    if filter_date:
        all_bookings = Booking.objects.filter(date=filter_date).order_by('time_slot__start_time')
    else:
        all_bookings = Booking.objects.all().order_by('-date', '-time_slot__start_time')
    
    context = {
        'all_bookings': all_bookings,
        'filter_date': filter_date
    }
    return render(request, 'lecturer_dashboard.html', context)

@login_required(login_url='/accounts/login/')
def export_bookings_excel(request):
    filter_date = request.GET.get('date')
    response = HttpResponse(content_type='text/csv')
    
    if filter_date:
        response['Content-Disposition'] = f'attachment; filename="Lab_Bookings_{filter_date}.csv"'
        bookings = Booking.objects.filter(date=filter_date).order_by('time_slot__start_time')
    else:
        response['Content-Disposition'] = 'attachment; filename="Lab_Bookings_All.csv"'
        bookings = Booking.objects.all().order_by('-date', '-time_slot__start_time')
        
    writer = csv.writer(response)
    writer.writerow(['Booked Date', 'Time Slot', 'Laptop No', 'Student Reg No', 'Attendance'])
    
    for booking in bookings:
        time_str = f"{booking.time_slot.start_time.strftime('%I:%M %p')} - {booking.time_slot.end_time.strftime('%I:%M %p')}"
        attendance_status = "Yes" if booking.attendance else "No"
        writer.writerow([booking.date, time_str, booking.laptop.lap_no, booking.student.reg_no, attendance_status])
        
    return response

# bookings/views.py
from .models import SpecialEvent

@login_required(login_url='/accounts/login/')
def manage_holidays_view(request):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    if request.method == 'POST':
        date = request.POST.get('date')
        event_type = request.POST.get('event_type')
        description = request.POST.get('description')
        
        SpecialEvent.objects.create(date=date, event_type=event_type, description=description)
        messages.success(request, "දිනය සාර්ථකව අවහිර කරන ලදී.")
        return redirect('manage_holidays')
        
    events = SpecialEvent.objects.all().order_by('-date')
    return render(request, 'manage_holidays.html', {'events': events})

@login_required(login_url='/accounts/login/')
def book_laptop_view(request):
    laptops = Laptop.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True)
    
    # වෙන්කළ නොහැකි දින (නිවාඩු/විභාග) Database එකෙන් ගෙන List එකක් ලෙස සකස් කිරීම
    blocked_events = SpecialEvent.objects.values_list('date', flat=True)
    blocked_dates_list = [date.strftime('%Y-%m-%d') for date in blocked_events]
    blocked_dates_json = json.dumps(blocked_dates_list) # Template එකට යැවීමට JSON බවට පත් කිරීම

    if request.method == 'POST':
        # (මෙතැන කලින් තිබූ POST request එකට අදාළ කේතය එලෙසම තබන්න)
        booking_date = request.POST.get('booking_date')
        time_slot_id = request.POST.get('time_slot')
        laptop_id = request.POST.get('laptop')

        is_blocked = SpecialEvent.objects.filter(date=booking_date).exists()
        if is_blocked:
            messages.error(request, "සමාවෙන්න! මෙම දිනයේ විභාගයක් හෝ විශේෂ නිවාඩුවක් ඇති බැවින් වෙන්කිරීම් කළ නොහැක.")
            return redirect('book_laptop')

        is_booked = Booking.objects.filter(date=booking_date, time_slot_id=time_slot_id, laptop_id=laptop_id).exists()
        if is_booked:
            messages.error(request, "මෙම ලැප්ටොප් යන්ත්‍රය අදාළ වේලාව සඳහා දැනටමත් වෙනත් සිසුවෙකු වෙන්කර ඇත.")
            return redirect('book_laptop')

        try:
            student_profile = request.user.student_profile
            Booking.objects.create(
                student=student_profile,
                laptop_id=laptop_id,
                date=booking_date,
                time_slot_id=time_slot_id
            )
            messages.success(request, "ඔබගේ වෙන්කිරීම සාර්ථකයි!")
            return redirect('student_dashboard')
        except request.user._meta.model.student_profile.RelatedObjectDoesNotExist:
            messages.error(request, "ඔබ Student ගිණුමකින් ලොග් වී නොමැත.")
            return redirect('book_laptop')

    context = {
        'laptops': laptops,
        'time_slots': time_slots,
        'blocked_dates_json': blocked_dates_json # මෙය අලුතින් context එකට එකතු විය
    }
    return render(request, 'book_laptop.html', context)

# 1. නිවාඩු දිනයක් සංස්කරණය කිරීම (Edit)
@login_required(login_url='/accounts/login/')
def edit_holiday_view(request, event_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    event = get_object_or_404(SpecialEvent, id=event_id)
    
    if request.method == 'POST':
        event.date = request.POST.get('date')
        event.event_type = request.POST.get('event_type')
        event.description = request.POST.get('description')
        event.save()
        messages.success(request, "අවහිර කළ දිනය සාර්ථකව යාවත්කාලීන කරන ලදී.")
        return redirect('manage_holidays')
        
    return render(request, 'edit_holiday.html', {'event': event})

# 2. නිවාඩු දිනයක් ඉවත් කිරීම (Delete)
@login_required(login_url='/accounts/login/')
def delete_holiday_view(request, event_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    event = get_object_or_404(SpecialEvent, id=event_id)
    event.delete()
    messages.success(request, "අවහිර කළ දිනය සාර්ථකව ඉවත් කරන ලදී.")
    return redirect('manage_holidays')