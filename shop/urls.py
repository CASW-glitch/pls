from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/logout/', LogoutView.as_view(next_page=None), name='logout'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('order-history/', views.order_history, name='order_history'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('process-order/', views.process_order, name='process_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
]

