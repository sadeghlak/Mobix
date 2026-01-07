from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Profile

# ------------------- ثبت‌نام -------------------
class CustomRegisterForm(UserCreationForm):
    """
    فرم ثبت‌نام کاربر
    فقط: username, email, password1, password2
    (نام کامل حذف شد - بعداً در پروفایل تکمیل می‌شود)
    """
    email = forms.EmailField(
        required=True,
        label=_('ایمیل'),
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
            'placeholder': 'example@email.com',
            'dir': 'ltr'
        }),
        help_text=_('برای بازیابی رمز عبور ضروری است')
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': 'نام کاربری',
                'dir': 'ltr'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # حذف help_textهای پیش‌فرض
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        
        # تنظیم placeholder برای رمز عبورها
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('رمز عبور'),
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition pr-12'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('تکرار رمز عبور'),
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition pr-12'
        })
    
    def clean_email(self):
        """بررسی یکتایی ایمیل"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('این ایمیل قبلاً ثبت شده است'))
        return email
    
    def clean_username(self):
        """بررسی یکتایی نام کاربری"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('این نام کاربری قبلاً ثبت شده است'))
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# ------------------- ورود -------------------
class CustomLoginForm(AuthenticationForm):
    """
    فرم ورود کاربر
    فقط با نام کاربری (نه ایمیل)
    """
    username = forms.CharField(
        label=_('نام کاربری'),
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
            'placeholder': 'نام کاربری خود را وارد کنید',
            'dir': 'ltr'
        })
    )
    
    password = forms.CharField(
        label=_('رمز عبور'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition pr-12',
            'placeholder': '••••••••',
        })
    )
    
    remember = forms.BooleanField(
        required=False,
        label=_('مرا به خاطر بسپار'),
        widget=forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
        })
    )

# ------------------- پروفایل -------------------
class ProfileUpdateForm(forms.ModelForm):
    """
    فرم ویرایش اطلاعات اصلی کاربر
    (first_name, last_name, email)
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': _('نام')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': _('نام خانوادگی')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': 'example@email.com',
                'dir': 'ltr'
            }),
        }
        
        labels = {
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
        }
    
    def clean_email(self):
        """بررسی یکتایی ایمیل (به جز کاربر فعلی)"""
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValidationError(_('این ایمیل قبلاً توسط کاربر دیگری ثبت شده است'))
        return email

class ProfileExtraForm(forms.ModelForm):
    """
    فرم تکمیل اطلاعات پروفایل
    (phone, address)
    """
    class Meta:
        model = Profile
        fields = ['phone', 'address']
        
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': '09123456789',
                'dir': 'ltr'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': _('آدرس کامل پستی'),
                'rows': 4
            }),
        }
        
        labels = {
            'phone': _('تلفن همراه'),
            'address': _('آدرس'),
        }
    
    def clean_phone(self):
        """اعتبارسنجی شماره تلفن"""
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # حذف فاصله و کاراکترهای غیرعددی
            phone = ''.join(filter(str.isdigit, phone))
            
            # بررسی طول و شروع
            if len(phone) != 11 or not phone.startswith('09'):
                raise ValidationError(_('شماره تلفن باید ۱۱ رقمی و با ۰۹ شروع شود'))
            
            # بررسی یکتایی (به جز پروفایل فعلی)
            profile_id = self.instance.id if self.instance else None
            if Profile.objects.filter(phone=phone).exclude(id=profile_id).exists():
                raise ValidationError(_('این شماره تلفن قبلاً ثبت شده است'))
        
        return phone