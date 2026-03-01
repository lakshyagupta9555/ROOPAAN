from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('inventory', 'Inventory Manager'),
        ('seller', 'Seller'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='inventory')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class TaxConfig(models.Model):
    cgst_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=9.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    sgst_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=9.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Tax Configuration"
        verbose_name_plural = "Tax Configurations"
    
    def __str__(self):
        return f"CGST: {self.cgst_rate}% | SGST: {self.sgst_rate}%"
    
    @property
    def total_gst(self):
        return self.cgst_rate + self.sgst_rate


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True, null=True, default="ROOPAAN'S")
    size = models.CharField(max_length=50, blank=True, null=True)
    colour = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    import_duty = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Set default brand if not provided
        if not self.brand:
            self.brand = "ROOPAAN'S"
        # Clean and normalize barcode before saving
        if self.barcode:
            self.barcode = str(self.barcode).strip()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} (₹{self.selling_price})"
    
    @property
    def profit_per_unit(self):
        return self.selling_price - self.cost_price - self.import_duty
    
    @property
    def is_in_stock(self):
        return self.quantity > 0


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sellers')
    
    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.IntegerField(null=True, blank=True)
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '₹'}"
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False, "Coupon is inactive"
        
        if now < self.valid_from:
            return False, "Coupon not yet valid"
        
        if now > self.valid_until:
            return False, "Coupon has expired"
        
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        return True, "Valid"
    
    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value
        
        return min(discount, subtotal)
