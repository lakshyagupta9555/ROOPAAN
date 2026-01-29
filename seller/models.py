from django.db import models
from inventory.models import Product, Seller, TaxConfig, Coupon
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, related_name='sales')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - ₹{self.total_amount}"
    
    @classmethod
    def generate_invoice_number(cls):
        from django.utils import timezone
        today = timezone.now()
        prefix = f"INV{today.strftime('%Y%m%d')}"
        
        last_invoice = cls.objects.filter(invoice_number__startswith=prefix).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"


class SaleItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)  # Store name at time of sale
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity
    
    @property
    def tax_amount(self):
        tax_rate = (self.sale.cgst_rate + self.sale.sgst_rate) / 100
        return self.subtotal * tax_rate
    
    @property
    def total(self):
        return self.subtotal + self.tax_amount
