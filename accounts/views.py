from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, StudentProfile, Batch

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

import csv
import io
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser, StudentProfile, Batch

# accounts/views.py
from django.shortcuts import get_object_or_404

def login_view(request):
    # දැනටමත් ලොග් වී ඇත්නම් මුල් පිටුවට යොමු කිරීම
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password =  request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # අදාළ භූමිකාව අනුව Dashboard එකට යොමු කිරීම (මෙම Dashboards අප මීළඟට සාදමු)
            if user.is_student:
                return redirect('student_dashboard') 
            elif user.is_lecturer:
                return redirect('lecturer_dashboard') # තාවකාලිකව lecturer_dashboard වෙත යොමු කර ඇත
            else:
                return redirect('home') # Admin සඳහා
        else:
            """messages.error(request, 'Username හෝ Password වැරදියි. කරුණාකර නැවත උත්සාහ කරන්න.')"""
            return redirect('student_dashboard')
            
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def student_signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    batches = Batch.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        reg_no = request.POST.get('reg_no')
        e_number = request.POST.get('e_number')
        programme = request.POST.get('programme')
        batch_id = request.POST.get('batch')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "මෙම Username එක දැනටමත් භාවිතයේ පවතී. කරුණාකර වෙනත් එකක් ලබා දෙන්න.")
            return redirect('student_signup')
            
        # 1. CustomUser ගිණුම සෑදීම
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_student=True
        )
        
        # 2. StudentProfile එක සෑදීම (is_approved=False ලෙස ස්වයංක්‍රීයව සැකසේ)
        batch = Batch.objects.get(id=batch_id)
        StudentProfile.objects.create(
            user=user,
            reg_no=reg_no,
            e_number=e_number,
            programme=programme,
            batch=batch,
            is_approved=False
        )
        
        messages.success(request, "ඔබගේ ලියාපදිංචිය සාර්ථකයි! කථිකාචාර්යවරයෙකු/Admin විසින් ඔබගේ ගිණුම අනුමත කළ පසු ඔබට ලැප්ටොප් වෙන්කළ හැක. කරුණාකර පද්ධතියට ලොග් වන්න.")
        return redirect('login')

    return render(request, 'student_signup.html', {'batches': batches})

@login_required(login_url='/accounts/login/')
def pending_students_view(request):
    # Admin හෝ Lecturer කෙනෙකුට පමණක් මෙම පිටුවට පිවිසීමට අවසර දීම
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = StudentProfile.objects.get(id=student_id)
        student.is_approved = True
        student.save()
        messages.success(request, f"{student.reg_no} සිසුවා සාර්ථකව අනුමත කරන ලදී.")
        return redirect('pending_students')
        
    pending_list = StudentProfile.objects.filter(is_approved=False)
    return render(request, 'pending_students.html', {'pending_list': pending_list})

@login_required(login_url='/accounts/login/')
def upload_students_csv(request):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "කරුණාකර .csv ආකෘතියේ ගොනුවක් පමණක් Upload කරන්න.")
            return redirect('upload_students')

        dataset = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(dataset)
        next(io_string) # Header පේළිය මඟ හැරීම

        success_count = 0
        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            try:
                username = row[0].strip()
                first_name = row[1].strip()
                last_name = row[2].strip()
                password = row[3].strip()
                reg_no = row[4].strip()
                e_number = row[5].strip()
                programme = row[6].strip()
                batch_name = row[7].strip()

                # Username එක දැනටමත් ඇත්දැයි බැලීම
                if CustomUser.objects.filter(username=username).exists():
                    continue

                # Batch එක ලබාගැනීම (නැතහොත් අලුතින් සෑදීම)
                batch, created = Batch.objects.get_or_create(name=batch_name, defaults={'dedicated_day': 0})

                # User සහ Profile සෑදීම (Upload කරන අය ස්වයංක්‍රීයව අනුමත වේ)
                user = CustomUser.objects.create_user(
                    username=username, password=password, first_name=first_name, last_name=last_name, is_student=True
                )
                StudentProfile.objects.create(
                    user=user, reg_no=reg_no, e_number=e_number, programme=programme, batch=batch, is_approved=True
                )
                success_count += 1
            except Exception as e:
                pass # දෝෂ සහිත පේළි මඟ හරී

        messages.success(request, f"සාර්ථකයි! සිසුන් {success_count} දෙනෙකු පද්ධතියට ඇතුළත් කරන ලදී.")
        return redirect('lecturer_dashboard')

    return render(request, 'upload_students.html')

@login_required(login_url='/accounts/login/')
def edit_student_view(request, student_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    student = get_object_or_404(StudentProfile, id=student_id)
    batches = Batch.objects.all()
    
    if request.method == 'POST':
        student.user.first_name = request.POST.get('first_name')
        student.user.last_name = request.POST.get('last_name')
        student.user.save()
        
        student.reg_no = request.POST.get('reg_no')
        student.e_number = request.POST.get('e_number')
        student.programme = request.POST.get('programme')
        student.batch_id = request.POST.get('batch')
        student.save()
        
        messages.success(request, "සිසුවාගේ තොරතුරු සාර්ථකව යාවත්කාලීන කරන ලදී.")
        return redirect('student_report') # වාර්තා පිටුවට යොමු කෙරේ
        
    return render(request, 'edit_student.html', {'student': student, 'batches': batches})

    from django.shortcuts import get_object_or_404 # මෙය ගොනුවේ ඉහළින්ම නොමැති නම් එක් කරන්න

# 1. කණ්ඩායම් බැලීම සහ අලුතින් එකතු කිරීම
@login_required(login_url='/accounts/login/')
def manage_batches_view(request):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        dedicated_day = request.POST.get('dedicated_day')
        
        if Batch.objects.filter(name=name).exists():
            messages.error(request, "මෙම නමින් කණ්ඩායමක් දැනටමත් පවතී.")
        else:
            Batch.objects.create(name=name, dedicated_day=dedicated_day)
            messages.success(request, "නව කණ්ඩායම සාර්ථකව පද්ධතියට එක් කරන ලදී.")
        return redirect('manage_batches')

    batches = Batch.objects.all()
    return render(request, 'manage_batches.html', {'batches': batches})

# 2. කණ්ඩායමක තොරතුරු වෙනස් කිරීම
@login_required(login_url='/accounts/login/')
def edit_batch_view(request, batch_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    batch = get_object_or_404(Batch, id=batch_id)
    
    if request.method == 'POST':
        batch.name = request.POST.get('name')
        batch.dedicated_day = request.POST.get('dedicated_day')
        batch.save()
        messages.success(request, "කණ්ඩායමේ තොරතුරු යාවත්කාලීන කරන ලදී.")
        return redirect('manage_batches')
        
    return render(request, 'edit_batch.html', {'batch': batch})

# 3. කණ්ඩායමක් ඉවත් කිරීම (Delete)
@login_required(login_url='/accounts/login/')
def delete_batch_view(request, batch_id):
    if not (request.user.is_lecturer or request.user.is_superuser):
        return redirect('home')
        
    batch = get_object_or_404(Batch, id=batch_id)
    batch.delete()
    messages.success(request, "කණ්ඩායම සාර්ථකව ඉවත් කරන ලදී.")
    return redirect('manage_batches')