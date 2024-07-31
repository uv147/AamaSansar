from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse_lazy
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.utils.text import slugify
from django.views.generic import CreateView, UpdateView

from store.OTP import sendOTPToUserForSignUp
from .models import *

from store.forms import ProductForm
from store.models import Product, Order, OrderItem


def handlesellersignup(request):
    if request.method == "GET":
        return render(request, 'registration/sellersignup.html')

    if request.method == 'POST':
        print(request.get_full_path())
        uname = request.POST.get('username')
        email = request.POST.get('email')
        # brand = request.POST.get('BrandName')
        # pan = request.POST.get('PAN')
        password = request.POST.get('pass1')
        confirmpassword = request.POST.get('pass2')
        if password != confirmpassword:
            messages.warning(request, "Password is Incorrect")
            return redirect('/vendor/seller-signup')
        try:
            if EcommerceUser.objects.get(username=uname):
                messages.info(request, 'UserName is Taken')
                return redirect('/vendor/seller')
        except:
            pass
        try:
            if EcommerceUser.objects.get(email=email):
                messages.info(request, 'Email is Taken')
                return redirect('/vendor/seller')
        except:
            pass
        # try:
        #     if EcommerceUser.objects.get(BrandName=brand):
        #         messages.info(request, 'BrandName is Taken')
        #         return redirect('/ecomadmin/seller')
        # except:
        #     pass
        # try:
        #     if EcommerceUser.objects.get(PAN=pan):
        #         messages.info(request, 'Pan is Taken')
        #         return redirect('/ecomadmin/seller')
        # except:
        #     pass

        is_vendor = False
        if request.get_full_path() == '/vendor/vendor-signup':
            is_vendor = True
        myuser = EcommerceUser.objects.create_user(uname, email, password, is_vendor=is_vendor)
        myuser.save()
        sendOTPToUserForSignUp(email=email)
        messages.success(request, 'Please verify your otp')
        return redirect('/otp-verify?value={}'.format(email))
    return render(request, 'registration/sellersignup.html')


# def handlesellerlogin(request):
#     if request.method == "GET":
#         return render(request, 'registration/sellerlogin.html')
#
#     if request.method == 'POST':
#         uname = request.POST.get('username')
#         pass1 = request.POST.get('pass1')
#         myuser = authenticate(username=uname, password=pass1)
#         if myuser is not None and myuser.is_vendor:
#             login(request, myuser)
#             messages.success(request, 'login success')
#             return redirect('/vendor/seller')
#         else:
#             messages.error(request, 'Invalid Credentials')
#             return redirect('/vendor/seller-login')
#     return render(request, 'registration/sellerlogin.html')


@login_required
def vendor_detail(request, pk):
    if request.user.is_authenticated and request.user.is_vendor:
        try:
            has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
            if has_vendor:
                vendor_detail = VendorDetail.objects.get(vendor_id=request.user.id)
                return render(request, 'userprofile/vendor_detail.html', {
                    'vendor_detail': vendor_detail,
                })
        except VendorDetail.DoesNotExist:
            return render(request, 'userprofile/vendor_detail_form.html')
    else:
        return render(request, 'registration/login.html')


@login_required
def seller(request, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_vendor:
        # products = request.user.products.exclude(status=Product.DELETED)
        try:
            if VendorDetail.objects.all():
                try:
                    has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
                    if has_vendor:
                        products = request.user.products.exclude(status=Product.DELETED)
                        order_items = OrderItem.objects.filter(product__user=request.user)
                        return render(request, 'userprofile/seller.html', {
                            'products': products,
                            'order_items': order_items,
                            'has_vendor': has_vendor
                        })
                except VendorDetail.DoesNotExist:
                    return render(request, 'userprofile/vendor_detail_form.html')

            else:
                return render(request, 'userprofile/vendor_detail_form.html')
        except:
            pass
    else:
        return render(request, 'registration/login.html')


@login_required
def seller_order_detail(request, user_pk, order_pk, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_vendor:
        try:
            has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
            if has_vendor:
                # order = get_object_or_404(Order, pk=order_pk)
                orderitem = OrderItem.objects.get(pk=order_pk)
                print("sdsd", orderitem)

                return render(request, 'userprofile/seller_order_detail.html', {
                    'orderitem': orderitem,
                })
        except VendorDetail.DoesNotExist:
            return render(request, 'userprofile/vendor_detail_form.html')
    else:
        return render(request, 'registration/login.html')


@login_required
def add_product(request, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_vendor:
        try:
            has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
            if has_vendor:
                if request.method == 'POST':
                    form = ProductForm(request.POST, request.FILES)

                    if form.is_valid():
                        title = request.POST.get('title')
                        product = form.save(commit=False)
                        product.user = request.user
                        product.slug = slugify(title)
                        product.save()

                        messages.success(request, 'The Product was added!')
                        return redirect('/vendor/' + str(request.user.id))
                    else:
                        print(form.errors)

                else:
                    form = ProductForm()

                return render(request, 'userprofile/add_product.html', {
                    'title': 'Add Product',
                    'form': form
                })
        except VendorDetail.DoesNotExist:
            return render(request, 'userprofile/vendor_detail_form.html')
    else:
        return render(request, 'registration/sellerlogin.html')


@login_required
def edit_product(request, user_pk, product_pk, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_vendor:
        try:
            has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
            if has_vendor:
                product = Product.objects.filter(user=request.user).get(pk=product_pk)
                if request.method == 'POST':
                    form = ProductForm(request.POST, request.FILES, instance=product)

                    if form.is_valid():
                        form.save()

                        messages.success(request, 'The Changes was added!')
                        return redirect('/vendor/' + str(request.user.id))

                else:
                    form = ProductForm(instance=product)
                    return render(request, 'userprofile/add_product.html', {
                        'title': 'Edit Product',
                        'product': product,
                        'form': form
                    })
        except VendorDetail.DoesNotExist:
            return render(request, 'userprofile/vendor_detail_form.html')
    else:
        return render(request, 'registration/sellerlogin.html')


@login_required
def delete_product(request, user_pk, product_pk, *args, **kwargs):
    if request.user.is_authenticated and request.user.is_vendor:
        try:
            has_vendor = VendorDetail.objects.get(vendor_id=request.user.id)
            if has_vendor:
                product = Product.objects.filter(user=request.user).get(pk=product_pk)
                product.status = Product.DELETED
                product.save()
                messages.success(request, 'The Product was deleted!')
                return redirect('/vendor/' + str(request.user.id))
        except VendorDetail.DoesNotExist:
            return render(request, 'userprofile/vendor_detail_form.html')
    else:
        return render(request, 'registration/sellerlogin.html')


class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_vendor


class SellerProfileView(LoginRequiredMixin, VendorRequiredMixin, CreateView):
    fields = ['company_name', 'company_address', 'company_phone', 'pan_vat_no',
              'company_registered_document', 'pan_vat_registered_document', 'vendor']
    model = VendorDetail

    def form_invalid(self, form):
        return render(self.request, 'forms/category_form.html', {
            'form': form,
        })

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('seller', kwargs={'pk': self.request.user.id})


class SellerProfileUpdateView(LoginRequiredMixin, VendorRequiredMixin, UpdateView):
    template_name = "userprofile/vendor_detail_update_form.html"
    fields = ['company_address', 'company_phone', 'company_registered_document']

    model = VendorDetail

    def form_invalid(self, form):
        return render(self.request, 'forms/category_form.html', {
            'form': form,
        })

    def get_queryset(self):
        return VendorDetail.objects.filter(id=self.kwargs.get('pk'))

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('seller', kwargs={'pk': self.request.user.id})
