from django.db import models
from django.utils import timezone
class Product(models.Model):
    Product_id = models.AutoField(primary_key=True)  # Set AutoField as primary key
    Product_name = models.CharField(max_length=50)
    desc = models.CharField(max_length=1000)
    price = models.IntegerField()
    category = models.CharField(max_length=50, default="")
    images = models.ImageField(upload_to="media/shop/images", default="")
    trending=models.CharField(max_length=6,default='false')

    def __str__(self):
        return self.Product_name 




class Order(models.Model):
    razorpay_order_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Assuming 'amount' is the correct field name
    payment_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
    
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    razorpay_order_id = models.CharField(max_length=255)  # Order ID from Razorpay
    razorpay_payment_id = models.CharField(max_length=255)  # Payment ID from Razorpay
    razorpay_signature = models.CharField(max_length=255)  # Payment signature
    payment_status = models.CharField(max_length=50, default="Pending")  # 'Success', 'Failed', etc.
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.payment_status}"
    
# models.py
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def total_price(self):
        return self.product.price * self.quantity
    def get_total_price(self):
        total = 0
        for item in self.cart_items.all():  # Assuming you have a relation with Cart model
            total += item.product.price * item.quantity
        return total