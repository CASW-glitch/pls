from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from .models import Product, Category, Review, Order, OrderItem, CartItem
from .forms import ReviewForm
from django.http import HttpResponse
from django.urls import reverse


def home(request):
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    selected_size = request.GET.get('size', 'M')

    if request.user.is_superuser and request.method == 'POST' and 'edit_product' in request.POST:
        product.name = request.POST.get('name', product.name)
        product.price = request.POST.get('price', product.price)
        product.description = request.POST.get('description', product.description)
        product.save()
        return redirect('product_detail', pk=pk)

    user_review = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            review_id = request.GET.get('review_id')
            if review_id:
                user_review = get_object_or_404(Review, pk=review_id, product=product)
        else:
            user_review = Review.objects.filter(product=product, user=request.user).first()

        if request.method == 'POST' and 'edit_product' not in request.POST:
            if user_review:
                form = ReviewForm(request.POST, instance=user_review)
            else:
                form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                if not user_review:
                    review.user = request.user
                review.save()
                return redirect('product_detail', pk=pk)
        else:
            form = ReviewForm(instance=user_review)
    else:
        form = None

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
        'selected_size': selected_size,
    })




@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if review.user == request.user or request.user.is_superuser:
        product_id = review.product.id
        review.delete()
        return redirect('product_detail', pk=product_id)


@login_required
def checkout(request):
    if request.method == 'POST':
        actions = ['remove_item_id', 'empty_cart', 'increase_item_id', 'decrease_item_id']
        for action in actions:
            if action in request.POST:
                item_id = request.POST.get(action)
                if action == 'empty_cart':
                    CartItem.objects.filter(user=request.user).delete()
                elif action == 'remove_item_id':
                    CartItem.objects.filter(id=item_id, user=request.user).delete()
                else:
                    cart_item = CartItem.objects.filter(id=item_id, user=request.user).first()
                    if cart_item:
                        if action == 'increase_item_id':
                            cart_item.quantity += 1
                        elif action == 'decrease_item_id':
                            cart_item.quantity = max(cart_item.quantity - 1, 0)
                        if cart_item.quantity == 0:
                            cart_item.delete()
                        else:
                            cart_item.save()
                return redirect('checkout')

    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.get_total_price() for item in cart_items)
    return render(request, "shop/checkout.html", {"cart_items": cart_items, "cart_total": cart_total})

@login_required
def process_order(request):
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, is_paid=False)
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('checkout')

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                size=item.size,
            )
        cart_items.delete()
        return redirect('order_success')

    return redirect('checkout')

@login_required
def order_success(request):
    return render(request, 'shop/order_success.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})


def about(request):
    categories = Category.objects.all()
    return render(request, 'about.html', {'categories': categories})

def contact(request):
    return render(request, 'contact.html')


@login_required
def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect('product_detail', pk=product_id)
    
    product = get_object_or_404(Product, pk=product_id)
    size = request.POST.get('size')
    
    if not size:
        return redirect('product_detail', pk=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        size=size, 
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect(f"{reverse('product_detail', kwargs={'pk': product.id})}?size={size}")
