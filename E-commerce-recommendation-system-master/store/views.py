from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .cart import Cart
from .forms import OrderForm
from .models import Category, Product, Order, OrderItem, Review

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('frontpage')

def change_quantity(request, product_id):
    action = request.GET.get('action','')

    if action:
        quantity = 1

        if action == 'decrease':
            quantity = -1
        
        cart = Cart(request)
        cart.add(product_id, quantity, True)

    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart_view')
  
def cart_view(request):
    cart = Cart(request)

    return render(request, 'store/cart_view.html',{
        'cart' : cart
    })

@login_required
def checkout(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            total_price = 0

            for item in cart:
                product = item['product']
                print(product.price)
                print(int(item['quantity']))
                total_price += product.price * int(item['quantity'])

            order = form.save(commit=False)
            order.created_by = request.user
            order.paid_amount = total_price
            order.save()

            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity
                
                item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
            cart.clear()

        return redirect('seller')
    else:
        form = OrderForm()

    return render(request, 'store/checkout.html',{
        'cart': cart,
        'form': form,
    })

def login(request):
    products = Product.objects.filter(status=Product.ACTIVE)[0:6]
    return render(request, 'store/login.html',{
        'products': products
    })  



def search(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(status=Product.ACTIVE).filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(request, 'store/search.html',{
        'query': query,
        'products': products,
    })

    
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(status=Product.ACTIVE)
    return render(request, 'store/category_detail.html',{
        'category': category,
        'products': products,
    }) 

def product_detail(request, category_slug, slug):
    
    product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE)

    if request.method == 'POST':
        rating = request.POST.get('rating', 3)
        content = request.POST.get('content', '')
        if content:
            reviews = Review.objects.filter(created_by=request.user, product=product)
            if reviews.count()> 0:
                review = reviews.first()
                review.rating = rating
                review.content = content
                review.save()
            else:
              review = Review.objects.create(
                product=product,
                rating=rating,
                content=content,
                created_by=request.user
            )

    return render(request, 'store/product_detail.html',{
        'product': product,
    })
