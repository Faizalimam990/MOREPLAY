from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.Userlogin, name='login'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('signup/', views.usersignup, name='signup'),
    path('products/<int:myid>', views.productview, name='productview'),
    path('products/<int:myid>/', views.productview, name='productview'),
    path('category/<str:category_name>/', views.category_view, name='category_view'),
    path('buy-now/', views.buy_now, name='buy_now'),
    path('category/<str:category_name>/', views.category_view, name='category_view'),
    # path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Add this line
    path('cart/', views.cart, name='cart'),  # Add this line
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
     path('verify-payment/', views.verify_payment, name='verify_payment'),
  # Add this line

] + router.urls

# Add this to serve media files during development
if settings.DEBUG:  # Make sure this is inside the DEBUG check
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)