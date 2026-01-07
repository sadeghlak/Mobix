from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import CustomRegisterForm, CustomLoginForm, ProfileUpdateForm, ProfileExtraForm
from .models import Profile

def register_view(request):
    """
    ویو ثبت‌نام کاربر
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('🎉 حساب کاربری شما با موفقیت ایجاد شد!'))
            return redirect('home')
        else:
            # نمایش خطاها
            for field, errors in form.errors.items():
                for error in errors:
                    # نمایش label فیلد به جای نام فیلد
                    field_label = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_label}: {error}')
    else:
        form = CustomRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """
    ویو ورود کاربر
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # مدیریت گزینه "مرا به خاطر بسپار"
            if not form.cleaned_data.get('remember'):
                request.session.set_expiry(0)  # با بستن مرورگر logout شود
            
            messages.success(request, _(f'👋 خوش آمدید {user.username}!'))
            return redirect('home')
        else:
            messages.error(request, _('❌ نام کاربری یا رمز عبور اشتباه است.'))
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    ویو خروج کاربر
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, _('✅ شما با موفقیت از حساب کاربری خود خارج شدید.'))
        return redirect('home')
    
    return render(request, 'accounts/logout.html')

@login_required
def profile_view(request):
    """
    ویو پروفایل کاربری
    """
    user = request.user
    
    # مطمئن شویم پروفایل وجود دارد (سیگنال باید ایجاد کند)
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user)
        profile_extra_form = ProfileExtraForm(request.POST, instance=profile)
        
        if profile_form.is_valid() and profile_extra_form.is_valid():
            profile_form.save()
            profile_extra_form.save()
            messages.success(request, _('✅ اطلاعات پروفایل با موفقیت به‌روزرسانی شد.'))
            return redirect('profile')
        else:
            # نمایش خطاهای فرم
            all_errors = []
            for form_instance in [profile_form, profile_extra_form]:
                for field, errors in form_instance.errors.items():
                    for error in errors:
                        field_label = form_instance.fields[field].label if field in form_instance.fields else field
                        all_errors.append(f'{field_label}: {error}')
            
            for error in all_errors:
                messages.error(request, error)
    
    else:
        profile_form = ProfileUpdateForm(instance=user)
        profile_extra_form = ProfileExtraForm(instance=profile)
    
    # آمار برای پیشخوان (موقت)
    stats = {
        'total_orders': 0,
        'pending_orders': 0,
        'completed_orders': 0,
    }
    
    context = {
        'profile_form': profile_form,
        'profile_extra_form': profile_extra_form,
        'stats': stats,
        'user': user,
        'user_profile': profile,
    }
    
    return render(request, 'accounts/profile.html', context)

# ویو اضافی برای نمایش سفارشات (آماده برای آینده)
@login_required
def orders_view(request):
    context = {
        'orders': [],
    }
    return render(request, 'accounts/orders.html', context)