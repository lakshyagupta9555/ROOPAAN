from django import forms
from .models import Product, TaxConfig, Coupon, User, Seller
from django.contrib.auth.password_validation import validate_password


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'quantity', 'selling_price', 'cost_price', 'import_duty', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
            'barcode': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
            'selling_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'import_duty': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
        }


class SellerForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'})
    )
    employee_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Seller.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('Employee ID already exists.')
        return employee_id
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password


class TaxConfigForm(forms.ModelForm):
    class Meta:
        model = TaxConfig
        fields = ['cgst_rate', 'sgst_rate']
        widgets = {
            'cgst_rate': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'sgst_rate': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'min_purchase_amount', 'max_discount_amount', 
                  'is_active', 'valid_from', 'valid_until', 'usage_limit']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
            'discount_type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
            'discount_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white', 'type': 'datetime-local'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-white'}),
        }
