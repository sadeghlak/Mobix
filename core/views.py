from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def home_view(request):
    return render(request, 'core/home.html')

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # ذخیره در دیتابیس
            messages.success(request, '✅ پیام شما با موفقیت ارسال شد.')
            return redirect('contact')
        else:
            messages.error(request, '❌ لطفا خطاهای فرم را برطرف کنید.')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

def privacy_view(request):
    return render(request, 'core/privacy.html')

def terms_view(request):
    return render(request, 'core/terms.html')

def privacy_view(request):
    return render(request, 'core/privacy.html')  