from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import ContactMessage  # مدل پیام‌های تماس
from django.contrib.auth.models import User
from django.db.models import Q
from core.models import ContactMessage
from accounts.models import Profile
from accounts.forms import CustomRegisterForm, ProfileUpdateForm, ProfileExtraForm
from django.contrib.auth.forms import UserCreationForm
import json
from blog.models import Article 
from blog.models import Article, CATEGORY_CHOICES, STATUS_CHOICES
import os
from datetime import datetime
from django.utils import timezone



@login_required
def admin_dashboard(request):
    """
    صفحه اصلی پنل مدیریت
    فقط برای کاربرانی که is_staff=True دارند
    """
    # بررسی آیا کاربر مدیر است
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به پنل مدیریت را ندارید.')
        return redirect('home')
    
    # داده‌های نمونه برای داشبورد
    context = {
        'page_title': 'پیشخوان مدیریت',
        'total_orders': 1248,
        'pending_orders': 42,
        'completed_orders': 1189,
        'recent_orders': [
            # داده‌های نمونه
        ]
    }
    
    return render(request, 'dashboard/index.html', context)


# ==================== صفحه مدیریت پیام‌های تماس ====================
@login_required
def contact_messages_list(request):
    """
    نمایش لیست پیام‌های تماس در داشبورد
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    # دریافت پارامترهای فیلتر
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # فیلتر اولیه
    messages_qs = ContactMessage.objects.all().order_by('-created_at')
    
    # اعمال فیلتر وضعیت
    if status_filter == 'read':
        messages_qs = messages_qs.filter(is_read=True)
    elif status_filter == 'unread':
        messages_qs = messages_qs.filter(is_read=False)
    
    # اعمال جستجو
    if search_query:
        messages_qs = messages_qs.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # آمار
    total_messages = messages_qs.count()
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    # صفحه‌بندی
    paginator = Paginator(messages_qs, 10)  # 10 پیام در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'پیام‌های تماس',
        'messages_list': page_obj,
        'total_messages': total_messages,
        'unread_count': unread_count,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/contact_messages.html', context)

# ==================== تغییر وضعیت خوانده شده ====================
@login_required
@require_POST
def toggle_message_read(request, message_id):
    """
    تغییر وضعیت خوانده/نخوانده بودن پیام
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'})
    
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = not message.is_read
    message.save()
    
    messages.success(request, f'✅ وضعیت پیام "{message.full_name}" به روز شد.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_read': message.is_read,
            'message_id': message_id
        })
    
    return redirect('contact_messages_list')

# ==================== دریافت محتوای کامل پیام (AJAX) ====================
@login_required
def get_message_content(request, message_id):
    """
    دریافت محتوای کامل پیام برای نمایش در مودال (AJAX)
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)
    
    message = get_object_or_404(ContactMessage, id=message_id)
    
    return JsonResponse({
        'id': message.id,
        'full_name': message.full_name,
        'email': message.email,
        'subject': message.get_subject_display(),
        'message': message.message,
        'created_at': message.created_at.strftime('%Y/%m/%d - %H:%M'),
        'is_read': message.is_read,
    })

# ==================== حذف پیام ====================
@login_required
@require_POST
def delete_message(request, message_id):
    """
    حذف یک پیام
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('contact_messages_list')
    
    message = get_object_or_404(ContactMessage, id=message_id)
    sender_name = message.full_name
    message.delete()
    
    messages.success(request, f'✅ پیام "{sender_name}" با موفقیت حذف شد.')
    return redirect('contact_messages_list')

# ==================== علامت‌گذاری همه به عنوان خوانده شده ====================
@login_required
@require_POST
def mark_all_as_read(request):
    """
    علامت‌گذاری همه پیام‌ها به عنوان خوانده شده
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('contact_messages_list')
    
    unread_messages = ContactMessage.objects.filter(is_read=False)
    count = unread_messages.count()
    unread_messages.update(is_read=True)
    
    messages.success(request, f'✅ {count} پیام به عنوان خوانده شده علامت‌گذاری شدند.')
    return redirect('contact_messages_list')

# ==================== حذف پیام‌های خوانده شده ====================
@login_required
@require_POST
def delete_read_messages(request):
    """
    حذف همه پیام‌های خوانده شده
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('contact_messages_list')
    
    read_messages = ContactMessage.objects.filter(is_read=True)
    count = read_messages.count()
    read_messages.delete()
    
    messages.success(request, f'✅ {count} پیام خوانده شده حذف شدند.')
    return redirect('contact_messages_list')

# ==================== پاسخ به پیام ====================
@login_required
def reply_to_message(request, message_id):
    """
    صفحه پاسخ به پیام
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('contact_messages_list')
    
    message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        # در آینده می‌توان سیستم ارسال ایمیل داخلی اضافه کرد
        reply_text = request.POST.get('reply_text', '')
        # TODO: ارسال ایمیل پاسخ
        
        messages.success(request, f'✅ پاسخ به {message.full_name} ارسال شد.')
        return redirect('contact_messages_list')
    
    context = {
        'page_title': 'پاسخ به پیام',
        'message': message,
    }
    
    return render(request, 'dashboard/reply_message.html', context)




# ==================== لیست کاربران ====================
@login_required
def users_list(request):
    """
    نمایش لیست کاربران در داشبورد
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    # دریافت پارامترهای فیلتر
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    role_filter = request.GET.get('role', 'all')
    per_page = int(request.GET.get('per_page', 10))
    
    # فیلتر اولیه
    users_qs = User.objects.all().order_by('-date_joined')
    
    # اعمال جستجو
    if search_query:
        users_qs = users_qs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(profile__phone__icontains=search_query)
        ).distinct()
    
    # اعمال فیلتر وضعیت
    if status_filter == 'active':
        users_qs = users_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        users_qs = users_qs.filter(is_active=False)
    
    # اعمال فیلتر نقش
    if role_filter == 'staff':
        users_qs = users_qs.filter(is_staff=True)
    elif role_filter == 'user':
        users_qs = users_qs.filter(is_staff=False)
    
    # آمار
    total_users = users_qs.count()
    staff_count = User.objects.filter(is_staff=True).count()
    
    # صفحه‌بندی
    paginator = Paginator(users_qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'مدیریت کاربران',
        'users_list': page_obj,
        'total_users': total_users,
        'staff_count': staff_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'per_page': per_page,
    }
    
    return render(request, 'dashboard/users_list.html', context)

# ==================== افزودن کاربر جدید ====================
@login_required
def add_user(request):
    """
    افزودن کاربر جدید به صورت دستی
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # فرم اصلی کاربر
        user_form = CustomRegisterForm(request.POST)
        
        # ایجاد instance اولیه برای فرم پروفایل
        profile_form_data = {
            'phone': request.POST.get('phone', ''),
            'address': request.POST.get('address', ''),
        }
        
        if user_form.is_valid():
            # ذخیره کاربر
            user = user_form.save()
            
            # تنظیم دسترسی‌ها
            user.is_active = request.POST.get('is_active') == 'true'
            user.is_staff = request.POST.get('is_staff') == 'true'
            user.is_superuser = request.POST.get('is_superuser') == 'true'
            user.save()
            
            # به‌روزرسانی پروفایل
            profile = user.profile
            profile.phone = profile_form_data['phone']
            profile.address = profile_form_data['address']
            profile.save()
            
            # پیام موفقیت
            messages.success(request, f'✅ کاربر "{user.username}" با موفقیت ایجاد شد.')
            
            # تصمیم گیری برای ریدایرکت
            if 'save_and_add' in request.POST:
                return redirect('add_user')
            elif 'save_and_view' in request.POST:
                return redirect('user_detail', user_id=user.id)
            else:
                return redirect('users_list')
        
        else:
            # نمایش خطاهای فرم
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        user_form = CustomRegisterForm()
    
    context = {
        'page_title': 'افزودن کاربر',
        'form': user_form,
    }
    
    return render(request, 'dashboard/add_user.html', context)

# ==================== تغییر وضعیت فعال/غیرفعال کاربر ====================
@login_required
@require_POST
def toggle_user_active(request, user_id):
    """
    تغییر وضعیت فعال/غیرفعال کاربر
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # نمی‌توان وضعیت خود کاربر را تغییر داد
    if user == request.user:
        messages.error(request, '❌ نمی‌توانید وضعیت حساب خود را تغییر دهید.')
        return redirect('users_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'فعال' if user.is_active else 'غیرفعال'
    messages.success(request, f'✅ وضعیت کاربر "{user.username}" به "{status}" تغییر یافت.')
    
    return redirect('users_list')

# ==================== تغییر نقش مدیر ====================
@login_required
@require_POST
def toggle_user_staff(request, user_id):
    """
    تغییر نقش کاربر به مدیر یا برعکس
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # نمی‌توان نقش خود را تغییر داد
    if user == request.user:
        messages.error(request, '❌ نمی‌توانید نقش خود را تغییر دهید.')
        return redirect('users_list')
    
    user.is_staff = not user.is_staff
    user.save()
    
    role = 'مدیر' if user.is_staff else 'کاربر عادی'
    messages.success(request, f'✅ نقش کاربر "{user.username}" به "{role}" تغییر یافت.')
    
    return redirect('users_list')

# ==================== حذف کاربر ====================
@login_required
@require_POST
def delete_user(request, user_id):
    """
    حذف کاربر از سیستم
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # نمی‌توان خود کاربر را حذف کرد
    if user == request.user:
        messages.error(request, '❌ نمی‌توانید حساب خود را حذف کنید.')
        return redirect('users_list')
    
    username = user.username
    user.delete()
    
    messages.success(request, f'✅ کاربر "{username}" با موفقیت حذف شد.')
    return redirect('users_list')

# ==================== مشاهده جزئیات کاربر ====================
@login_required
def user_detail(request, user_id):
    """
    مشاهده جزئیات کامل یک کاربر
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'page_title': f'مشاهده کاربر - {user.username}',
        'user': user,
    }
    
    return render(request, 'dashboard/user_detail.html', context)

# ==================== ویرایش کاربر ====================
@login_required
def edit_user(request, user_id):
    """
    ویرایش اطلاعات کاربر
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = ProfileExtraForm(request.POST, instance=user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # به‌روزرسانی دسترسی‌ها
            if 'is_active' in request.POST:
                user.is_active = request.POST.get('is_active') == 'true'
            if 'is_staff' in request.POST:
                user.is_staff = request.POST.get('is_staff') == 'true'
            if 'is_superuser' in request.POST:
                user.is_superuser = request.POST.get('is_superuser') == 'true'
            user.save()
            
            messages.success(request, f'✅ اطلاعات کاربر "{user.username}" با موفقیت به‌روزرسانی شد.')
            return redirect('user_detail', user_id=user.id)
        
        else:
            # نمایش خطاها
            for form_instance in [user_form, profile_form]:
                for field, errors in form_instance.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = ProfileExtraForm(instance=user.profile)
    
    context = {
        'page_title': f'ویرایش کاربر - {user.username}',
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'dashboard/edit_user.html', context)

# ==================== عملیات گروهی روی کاربران ====================
@login_required
@require_POST
def bulk_users_action(request):
    """
    انجام عملیات گروهی روی کاربران انتخاب شده
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'})
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        user_ids = data.get('users', [])
        
        if not action or not user_ids:
            return JsonResponse({'success': False, 'error': 'داده‌های ناقص'})
        
        # فیلتر کاربران (نمی‌توان روی خود کاربر عملیات انجام داد)
        users = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)
        
        if action == 'activate':
            users.update(is_active=True)
            message = f'✅ {users.count()} کاربر فعال شدند.'
        
        elif action == 'deactivate':
            users.update(is_active=False)
            message = f'✅ {users.count()} کاربر غیرفعال شدند.'
        
        elif action == 'make_staff':
            users.update(is_staff=True)
            message = f'✅ {users.count()} کاربر به مدیر تبدیل شدند.'
        
        elif action == 'remove_staff':
            users.update(is_staff=False)
            message = f'✅ {users.count()} کاربر از مدیران حذف شدند.'
        
        else:
            return JsonResponse({'success': False, 'error': 'عملیات نامعتبر'})
        
        return JsonResponse({'success': True, 'message': message})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== جستجوی سریع کاربران (AJAX) ====================
@login_required
def search_users_ajax(request):
    """
    جستجوی سریع کاربران برای اتوکامپلیت
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)
    
    query = request.GET.get('q', '')
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:10]
        
        results = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name() or user.username,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            }
            for user in users
        ]
    else:
        results = []
    
    return JsonResponse({'results': results})


# ==================== مدیریت مقالات ====================

@login_required
def blog_list_view(request):
    """
    نمایش لیست مقالات در داشبورد
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    # دریافت پارامترهای فیلتر
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    per_page = int(request.GET.get('per_page', 10))
    
    # فیلتر اولیه
    articles_qs = Article.objects.all().order_by('-publish_date', '-created_at')
    
    # اعمال فیلتر وضعیت
    if status_filter == 'published':
        articles_qs = articles_qs.filter(status='published')
    elif status_filter == 'draft':
        articles_qs = articles_qs.filter(status='draft')
    
    # اعمال فیلتر دسته‌بندی
    if category_filter != 'all':
        articles_qs = articles_qs.filter(category=category_filter)
    
    # اعمال جستجو
    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )
    
    # آمار
    total_articles = articles_qs.count()
    published_count = Article.objects.filter(status='published').count()
    draft_count = Article.objects.filter(status='draft').count()
    
    # صفحه‌بندی
    paginator = Paginator(articles_qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'مدیریت مقالات',
        'articles_list': page_obj,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'category_choices': CATEGORY_CHOICES,
        'status_choices': STATUS_CHOICES,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'per_page': per_page,
    }
    
    return render(request, 'dashboard/blog_list.html', context)



    """
    ایجاد مقاله جدید با فرم Django
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # ذخیره مقاله
                article = form.save(commit=False)
                article.author = request.user
                
                # مدیریت وضعیت بر اساس دکمه کلیک شده
                if 'save_publish' in request.POST:
                    article.status = 'published'
                elif 'save_draft' in request.POST:
                    article.status = 'draft'
                
                article.save()
                
                # اعتبارسنجی تصویر
                if 'image' in request.FILES:
                    image_file = request.FILES['image']
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
                    ext = os.path.splitext(image_file.name)[1].lower()
                    
                    if ext not in valid_extensions:
                        messages.warning(request, 'فرمت تصویر باید یکی از موارد JPG, PNG, WebP, GIF باشد.')
                    elif image_file.size > 5 * 1024 * 1024:  # 5MB
                        messages.warning(request, 'حجم تصویر باید کمتر از ۵ مگابایت باشد.')
                
                # پیام موفقیت
                if article.status == 'published':
                    messages.success(request, f'مقاله "{article.title}" با موفقیت منتشر شد.')
                else:
                    messages.success(request, f'مقاله "{article.title}" به عنوان پیش‌نویس ذخیره شد.')
                
                # تصمیم‌گیری برای ریدایرکت
                if 'save_and_new' in request.POST:
                    return redirect('blog_create')
                else:
                    return redirect('blog_list')
                    
            except Exception as e:
                messages.error(request, f'خطا در ایجاد مقاله: {str(e)}')
                return redirect('blog_create')
        
        else:
            # نمایش خطاهای فرم
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_name}: {error}')
    
    else:
        # مقداردهی اولیه برای فرم
        form = ArticleForm(initial={
            'status': 'draft',
            'publish_date': timezone.now()
        })
    
    context = {
        'page_title': 'ایجاد مقاله جدید',
        'form': form,
        'category_choices': CATEGORY_CHOICES,
    }
    
    return render(request, 'dashboard/blog_create.html', context)


    """
    ایجاد مقاله جدید با فرم Django
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # ذخیره مقاله
                article = form.save(commit=False)
                article.author = request.user
                
                # مدیریت وضعیت بر اساس دکمه کلیک شده
                if 'save_publish' in request.POST:
                    article.status = 'published'
                elif 'save_draft' in request.POST:
                    article.status = 'draft'
                
                article.save()
                
                messages.success(request, f'مقاله "{article.title}" با موفقیت ذخیره شد.')
                return redirect('blog_list_view')  # مطمئن شوید نام view درست است
                    
            except Exception as e:
                messages.error(request, f'خطا در ایجاد مقاله: {str(e)}')
    else:
        # مقداردهی اولیه برای فرم
        form = ArticleForm()
    
    context = {
        'page_title': 'ایجاد مقاله جدید',
        'form': form,
        'category_choices': CATEGORY_CHOICES,
    }
    
    return render(request, 'dashboard/blog_create.html', context)

@login_required
def blog_create_view(request):
    """
    ایجاد مقاله جدید
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # دریافت داده‌های فرم
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        publish_date_str = request.POST.get('publish_date')
        
        # بررسی فیلدهای ضروری
        if not title or not content or not category:
            messages.error(request, 'لطفاً عنوان، محتوا و دسته‌بندی را پر کنید.')
            return redirect('blog_create')
        
        # مدیریت تاریخ انتشار
        if publish_date_str:
            try:
                # تبدیل تاریخ از فرمت HTML datetime-local
                publish_date = timezone.make_aware(
                    datetime.strptime(publish_date_str, '%Y-%m-%dT%H:%M')
                )
            except (ValueError, TypeError):
                publish_date = timezone.now()
        else:
            publish_date = timezone.now()
        
        # مدیریت وضعیت بر اساس دکمه کلیک شده
        if 'save_publish' in request.POST:
            status = 'published'
        elif 'save_draft' in request.POST:
            status = 'draft'
        
        try:
            # ایجاد مقاله
            article = Article.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user,
                status=status,
                publish_date=publish_date
            )
            
            # مدیریت آپلود عکس
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                
                # اعتبارسنجی فایل
                valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                ext = os.path.splitext(image_file.name)[1].lower()
                
                if ext in valid_extensions and image_file.size <= 5 * 1024 * 1024:  # 5MB
                    article.image = image_file
                    article.save()
                else:
                    messages.warning(request, 'تصویر باید کمتر از ۵MB و با فرمت مجاز باشد.')
            
            # پیام موفقیت
            if status == 'published':
                messages.success(request, f'مقاله "{title}" با موفقیت منتشر شد.')
            else:
                messages.success(request, f'مقاله "{title}" به عنوان پیش‌نویس ذخیره شد.')
            
            # تصمیم‌گیری برای ریدایرکت
            if 'save_and_new' in request.POST:
                return redirect('blog_create')
            else:
                return redirect('blog_list')
                
        except Exception as e:
            messages.error(request, f'خطا در ایجاد مقاله: {str(e)}')
            return redirect('blog_create')
    
    # برای GET request
    context = {
        'page_title': 'ایجاد مقاله جدید',
        'category_choices': CATEGORY_CHOICES,
        'status_choices': STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/blog_create.html', context)

@login_required
def blog_detail_view(request, article_id):
    """
    مشاهده جزئیات مقاله
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    article = get_object_or_404(Article, id=article_id)
    
    context = {
        'page_title': f'مقاله - {article.title}',
        'article': article,
    }
    
    return render(request, 'dashboard/blog_detail.html', context)


@login_required
def blog_edit_view(request, article_id):
    """
    ویرایش مقاله
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        # TODO: بعداً فرم رو کامل می‌کنیم
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        status = request.POST.get('status')
        
        if title and content and category and status:
            article.title = title
            article.content = content
            article.category = category
            article.status = status
            article.save()
            
            messages.success(request, f'مقاله "{title}" با موفقیت ویرایش شد.')
            return redirect('blog_detail', article_id=article.id)
        else:
            messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید.')
    
    context = {
        'page_title': f'ویرایش مقاله - {article.title}',
        'article': article,
        'category_choices': CATEGORY_CHOICES,
        'status_choices': STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/blog_edit.html', context)


@login_required
@require_POST
def blog_delete_view(request, article_id):
    """
    حذف مقاله
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('blog_list')
    
    article = get_object_or_404(Article, id=article_id)
    title = article.title
    article.delete()
    
    messages.success(request, f'مقاله "{title}" با موفقیت حذف شد.')
    return redirect('blog_list')


@login_required
@require_POST
def toggle_article_status(request, article_id):
    """
    تغییر وضعیت مقاله (پیش‌نویس/منتشر شده)
    """
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('blog_list')
    
    article = get_object_or_404(Article, id=article_id)
    
    # تغییر وضعیت
    if article.status == 'draft':
        article.status = 'published'
        status_fa = 'منتشر شده'
    else:
        article.status = 'draft'
        status_fa = 'پیش‌نویس'
    
    article.save()
    
    messages.success(request, f'✅ وضعیت مقاله "{article.title}" به "{status_fa}" تغییر یافت.')
    return redirect('blog_list')


@login_required
@require_POST
def bulk_articles_action(request):
    """
    انجام عملیات گروهی روی مقالات انتخاب شده
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'دسترسی غیرمجاز'})
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        article_ids = data.get('articles', [])
        
        if not action or not article_ids:
            return JsonResponse({'success': False, 'error': 'داده‌های ناقص'})
        
        # فیلتر مقالات
        articles = Article.objects.filter(id__in=article_ids)
        
        if action == 'publish':
            articles.update(status='published')
            message = f'✅ {articles.count()} مقاله منتشر شدند.'
        
        elif action == 'draft':
            articles.update(status='draft')
            message = f'✅ {articles.count()} مقاله به پیش‌نویس تغییر یافتند.'
        
        elif action == 'delete':
            count = articles.count()
            articles.delete()
            message = f'✅ {count} مقاله حذف شدند.'
        
        else:
            return JsonResponse({'success': False, 'error': 'عملیات نامعتبر'})
        
        return JsonResponse({'success': True, 'message': message})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    """
    نمایش لیست مقالات در داشبورد
    """
    if not request.user.is_staff:
        messages.error(request, 'شما دسترسی به این بخش را ندارید.')
        return redirect('admin_dashboard')
    
    # دریافت پارامترهای فیلتر
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    per_page = int(request.GET.get('per_page', 10))
    
    # فیلتر اولیه
    articles_qs = Article.objects.all().order_by('-publish_date', '-created_at')
    
    # اعمال فیلتر وضعیت
    if status_filter == 'published':
        articles_qs = articles_qs.filter(status='published')
    elif status_filter == 'draft':
        articles_qs = articles_qs.filter(status='draft')
    
    # اعمال فیلتر دسته‌بندی
    if category_filter != 'all':
        articles_qs = articles_qs.filter(category=category_filter)
    
    # اعمال جستجو
    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )
    
    # آمار
    total_articles = articles_qs.count()
    published_count = Article.objects.filter(status='published').count()
    draft_count = Article.objects.filter(status='draft').count()
    
    # صفحه‌بندی
    paginator = Paginator(articles_qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # دسته‌بندی‌ها برای فیلتر
    from blog.models import CATEGORY_CHOICES
    
    context = {
        'page_title': 'مدیریت مقالات',
        'articles_list': page_obj,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'category_choices': CATEGORY_CHOICES,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'per_page': per_page,
    }
    
    return render(request, 'dashboard/blog_list.html', context)