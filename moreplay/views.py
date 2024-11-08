from django.shortcuts import render,redirect
from .models import Product,Order
from rest_framework import viewsets
from .serializer import ProductSerializer
from django.http import JsonResponse
from .models import Product, Order,Payment
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Product, Order
from django.conf import settings
import razorpay

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))


from django.conf import settings
# View for the index page
def index(request):
    pob = Product.objects.all()
    products = Product.objects.filter(category='Headphones')
    print(products)
    
    return render(request, 'index.html', {'pob': pob})

# View for the About Us page
def aboutus(request):
    return render(request, 'about.html')

# View for product details
from django.shortcuts import get_object_or_404

def productview(request, myid):
    # Fetch the product using the ID, or return a 404 if it doesn't exist
    product = get_object_or_404(Product, Product_id=myid)
   
    return render(request, 'productview.html', {'product': product})

# View for user login
def Userlogin(request):
    return render(request, 'login.html')

# View for user signup
def usersignup(request):
    # if request.method == 'POST':
    #     fun = request.POST['first_name']
    #     lun = request.POST['last_name']
    #     ueml = request.POST['u_email']
    #     uphn = request.POST['u_phone']
    #     upass = request.POST['u_password']
        
    #     uobj = Userprofile(First_Name=fun, last_name=lun, user_email=ueml, password=upass, phone_number=uphn)
    #     uobj.save()
    
    return render(request, 'signup.html')

# ViewSet for products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def category_view(request, category_name):
    # Fetch products in the specified category
    products = Product.objects.filter(category=category_name)
    categories = Product.objects.values_list('category', flat=True).distinct()
    print(f"Categories: {categories}")
    
    # Build the breadcrumb for the category page
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': category_name, 'url': f'/category/{category_name}/'}  # Fix the URL to include the category name
    ]
    
    return render(request, 'category.html', {'products': products, 'category_name': category_name, 'breadcrumbs': breadcrumbs,'categories': categories })


# Buy Now View# Buy Now View (Updated to handle all cart products)
# Create a Razorpay Order in the buy_now view

# def buy_now(request):
#     product_ids = request.GET.get('product_ids', '')

#     if not product_ids:
#         raise Http404("No products selected")

#     product_ids = product_ids.split(',')

#     cart = request.session.get('cart', {})

#     if not cart:
#         return redirect('index')  # Redirect to home if cart is empty

#     cart_with_totals = []
#     total_price = 0
#     for product_id in product_ids:
#         item = cart.get(product_id, {})
#         try:
#             product_instance = get_object_or_404(Product, Product_id=product_id)
#             price = item.get('price', product_instance.price)
#             quantity = item.get('quantity', 1)

#             item['total_price'] = price * quantity
#             total_price += item['total_price']

#             if product_instance.images:
#                 item['image'] = product_instance.images.url
#             else:
#                 item['image'] = '/path/to/default-image.jpg'

#             cart_with_totals.append(item)

#         except Product.DoesNotExist:
#             continue

#     # Generate Razorpay Order ID
#     razorpay_order = razorpay_client.order.create({
#         'amount': total_price * 100,  # Amount in paise (INR * 100)
#         'currency': 'INR',
#         'payment_capture': 1  # Auto-capture the payment
#     })

#     razorpay_order_id = razorpay_order['id']  # Get the Razorpay order ID
#     razorpay_key = "rzp_test_qBHckndkmksNNr"  # Your Razorpay key

#     context = {
#         'cart': cart_with_totals,
#         'order_amount': total_price,
#         'order_amount_in_paise': total_price * 100,  # Amount in paise for Razorpay
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_key': razorpay_key,
#     }

#     return render(request, 'buy_now.html', context)

def buy_now(request):
    product_ids = request.GET.get('product_ids', '')

    if not product_ids:
        raise Http404("No products selected")

    # Convert product_ids to a list
    product_ids = product_ids.split(',')

    # Get the cart from the session
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('index')  # Redirect to home if cart is empty

    cart_with_totals = []
    total_price = 0

    for product_id in product_ids:
        item = cart.get(product_id, {})
        try:
            product_instance = get_object_or_404(Product, Product_id=product_id)
            price = item.get('price', product_instance.price)
            quantity = item.get('quantity', 1)

            item['total_price'] = price * quantity
            total_price += item['total_price']

            if product_instance.images:
                item['image'] = product_instance.images.url
            else:
                item['image'] = '/path/to/default-image.jpg'

            cart_with_totals.append(item)

        except Product.DoesNotExist:
            continue

    # Generate Razorpay Order
    razorpay_order = razorpay_client.order.create({
        'amount': total_price * 100,  # Amount in paise (Razorpay expects the amount in paise)
        'currency': 'INR',
        'payment_capture': 1  # Auto-capture the payment
    })

    razorpay_order_id = razorpay_order['id']  # Get the Razorpay order ID
    razorpay_key = settings.RAZORPAY_API_KEY  # Your Razorpay key

    # Save the order in the database
    order = Order.objects.create(
        razorpay_order_id=razorpay_order_id,
        amount=total_price,  # Store the total amount (in INR, not paise)
        payment_status='Pending'
    )

    context = {
        'cart': cart_with_totals,
        'order_amount': total_price,  # Total amount to be paid (INR)
        'order_amount_in_paise': total_price * 100,  # Amount in paise for Razorpay
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': razorpay_key,
    }

    return render(request, 'buy_now.html', context)


#######-----------------------Custom Filter------------------------------>
# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies the value by the given argument (arg)."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
# import json
# @csrf_exempt  # Exempt CSRF check for the callback URL, since it's called from the client-side
# def payment_callback(request):
#     if request.method == 'POST':
#         try:
#             # Get payment details from the request
#             payment_data = json.loads(request.body)
#             payment_id = payment_data.get('razorpay_payment_id')
#             order_id = payment_data.get('razorpay_order_id')
#             signature = payment_data.get('razorpay_signature')

#             # Verify the signature
#             params_dict = {
#                 'razorpay_order_id': order_id,
#                 'razorpay_payment_id': payment_id
#             }

#             try:
#                 # Verify the signature
#                 razorpay_client.utility.verify_payment_signature(params_dict, signature)
                
#                 # If signature is verified, mark the payment as successful
#                 order = Order.objects.get(order_id=order_id)
#                 payment = Payment.objects.create(
#                     order=order,
#                     payment_id=payment_id,
#                     amount=order.total_price,
#                     status='success'
#                 )

#                 # Optionally update the order status in your database
#                 order.status = 'paid'
#                 order.save()

#                 return JsonResponse({'status': 'success'})
#             except razorpay.errors.SignatureVerificationError:
#                 # If the signature is not valid, respond with failure
#                 return JsonResponse({'status': 'failure', 'message': 'Signature verification failed'}, status=400)
#         except Exception as e:
#             return JsonResponse({'status': 'failure', 'message': str(e)}, status=500)
#     else:
#         return JsonResponse({'status': 'failure', 'message': 'Invalid request method'}, status=400)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt  # This is necessary to handle POST requests from Razorpay callback
@require_POST  # Ensure that this view only accepts POST requests
def verify_payment(request):
    try:
        # Parse the JSON data received from the frontend
        payment_details = json.loads(request.body)

        payment_id = payment_details['razorpay_payment_id']
        order_id = payment_details['razorpay_order_id']
        signature = payment_details['razorpay_signature']

        # Verify the payment signature using Razorpay's utility
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        razorpay_client.utility.verify_payment_signature(params_dict)

        # If signature is verified, update the order status in the database
        order = Order.objects.get(razorpay_order_id=order_id)
        order.payment_status = 'Paid'  # Update payment status to "Paid"
        order.save()

        # Optionally, you can log the payment details or take other actions (like sending a receipt email)
        return JsonResponse({'status': 'success'})

    except razorpay.errors.SignatureVerificationError as e:
        # If signature verification fails
        return JsonResponse({'status': 'failure', 'error': 'Signature verification failed'})

    except Order.DoesNotExist:
        # If the order doesn't exist in the database
        return JsonResponse({'status': 'failure', 'error': 'Order not found'})

    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({'status': 'failure', 'error': str(e)})

# Add to cart view# Add item to cart view (add_to_cart)
def add_to_cart(request, product_id):
    # Get the product or return a 404 error if the product does not exist
    product = get_object_or_404(Product, Product_id=product_id)

    # Get the current cart from the session (if any)
    cart = request.session.get('cart', {})

    # If the product is already in the cart, just update the quantity
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        # Otherwise, add the product to the cart
        cart[str(product_id)] = {
            'name': product.Product_name,
            'price': product.price,
            'quantity': 1,
            'image': product.images.url if product.images else '/path/to/default-image.jpg'
        }

    # Save the updated cart back into the session
    request.session['cart'] = cart

    # Redirect the user to the cart page after adding the item
    return redirect('cart')
# View to display the cart
def cart(request):
    # Get the cart from the session
    cart = request.session.get('cart', {})

    # List to hold the product details
    cart_items = []
    total_price = 0

    # Loop through the items in the cart and calculate prices
    for product_id, item in cart.items():
        # Fetch product details from the database
        try:
            product = Product.objects.get(Product_id=product_id)
            print(product.Product_id)

            # Calculate the total price for the item
            item['total_price'] = item['price'] * item['quantity']
            total_price += item['total_price']

            # Add product details to the item
            item['name'] = product.Product_name
            item['image'] = product.images.url if product.images else '/path/to/default-image.jpg'
            item['product_id'] = product.Product_id  # Ensure product_id is added for use in the template

            # Add the item to the cart_items list
            cart_items.append(item)
        except Product.DoesNotExist:
            # If the product is not found, you can choose to skip it or log an error
            continue

    # Ensure the checkout link uses all product IDs in the cart
    checkout_product_ids = list(cart.keys())  # List of all product IDs in the cart

    # Return the context to the template
    return render(request, 'cart.html', {
        'cart': cart_items,  # Pass the updated cart with product details
        'total_price': total_price,  # Total price of all items
        'checkout_product_ids': checkout_product_ids  # Pass all product IDs to the template
    })
# Remove from cart view
# views.py


def remove_from_cart(request, product_id):
    # Get the current cart from the session
    cart = request.session.get('cart', {})
    print(f"Cart before removal: {cart}")  # Debugging line

    # If the product is in the cart, remove it
    if str(product_id) in cart:
        del cart[str(product_id)]
        print(f"Removed product {product_id}")  # Debugging line
    else:
        print(f"Product {product_id} not found in cart")  # Debugging line

    # Save the updated cart back into the session
    request.session['cart'] = cart
    print(f"Updated cart: {request.session.get('cart')}")  # Debugging line

    # Redirect to the cart page after removing the item
    return redirect('cart')


