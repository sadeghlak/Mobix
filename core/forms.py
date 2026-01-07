from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': 'نام کامل خود را وارد کنید'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'placeholder': 'example@email.com'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition',
                'rows': 5,
                'placeholder': 'پیام خود را بنویسید...'
            }),
        }
        labels = {
            'full_name': 'نام و نام خانوادگی',
            'email': 'ایمیل',
            'subject': 'موضوع',
            'message': 'پیام شما',
        }
        