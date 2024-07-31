from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import Userprofile

from store.forms import ProductForm
from store.models import Product, Order, OrderItem


def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products = user.products.filter(status=Product.ACTIVE)

    return render(request, 'userprofile/vendor_detail.html',{
        'user': user,
        'products' : products,

    })
    
def seller(request):
    products = request.user.products.exclude(status=Product.DELETED)
    order_items = OrderItem.objects.filter(product__user=request.user)
    return render(request, 'userprofile/seller.html',{
        'products': products,
        'order_items': order_items,
    })

def seller_order_detail(request,pk):
    order = get_object_or_404(Order, pk=pk)

    return render(request, 'userprofile/seller_order_detail.html',{
        'order': order,
    })


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            title = request.POST.get('title')
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()

            messages.success(request, 'The Product was added!')
            return redirect('seller')

    else:
        form = ProductForm()

    return render(request, 'userprofile/add_product.html',{
        'title' : 'Add Product',
        'form' : form
    })
    
def edit_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            messages.success(request, 'The Changes was added!')
            return redirect('seller')

    else:
       form = ProductForm(instance=product)
    return render(request, 'userprofile/add_product.html',{
        'title' : 'Edit Product',
        'product' : product,
        'form' : form
    })

def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()

    messages.success(request, 'The Product was deleted!')
    return redirect('seller')
