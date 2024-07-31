import json

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, UpdateView, TemplateView, CreateView, DetailView

from ecomadmin.models import About
from recommendation.data_collection import hybrid_recommendation
from vendor.models import EcommerceUser
from .OTP import sendOTPToUserForSignUp, sendOTPToUserForForgotPassword
from .cart import Cart
from .forms import OrderForm, ProfileForm
from .models import Category, Product, Order, OrderItem, Review, CustomerProfile, UserOTP


def handlelogin(request):
    if request.method == "GET":
        return render(request, 'registration/login.html')

    elif request.method == "POST":
        uname = request.POST.get("username")
        pass1 = request.POST.get("pass1")
        myuser = authenticate(username=uname, password=pass1)
        if (myuser is not None and myuser.is_OTP_verified) or (myuser is not None and myuser.is_superuser):
            login(request, myuser)
            messages.success(request, "Login Success")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials or OTP not verified yet!!!")
            return redirect('/login')
    return render(request, 'registration/login.html')


def handlesignup(request):
    if request.method == "GET":
        return render(request, 'registration/signup.html')

    elif request.method == "POST":
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        confirmpassword = request.POST.get('pass2')
        # print(uname,email,password,confirmpassword)
        if password != confirmpassword:
            messages.warning(request, "Password is Incorrect")
            return redirect('/signup')
        try:
            if EcommerceUser.objects.get(username=uname):
                messages.info(request, 'UserName is Taken')
                return redirect('/signup')
        except:
            pass
        try:
            if EcommerceUser.objects.get(email=email):
                messages.info(request, 'Email is Taken')
                return redirect('/signup')
        except:
            pass
        myuser = EcommerceUser.objects.create_user(uname, email, password)
        myuser.save()
        sendOTPToUserForSignUp(email=email)
        messages.success(request, 'Please verify your otp')
        return redirect('/otp-verify?value={}'.format(email))
    return render(request, 'registration/signup.html')


def otp_verify(request):
    if request.method == 'POST':
        email = request.GET.get("value")
        first = request.POST.get('first')
        second = request.POST.get('second')
        third = request.POST.get('third')
        fourth = request.POST.get('fourth')
        fifth = request.POST.get('fifth')
        otp = first + second + third + fourth + fifth
        query = UserOTP.objects.filter(email=email)
        if query.exists():
            obj = query.get(is_active=True)
            if str(obj.otp) == str(otp):
                # Update the status of user
                user = EcommerceUser.objects.get(email=email)
                opt_status = UserOTP.objects.filter(email=user.email, is_active=True).last()
                if user:
                    # user = user.first()
                    user.is_OTP_verified = True
                    user.save()
                    opt_status.is_active = False
                    opt_status.save()
                    messages.success(request, "OTP verification successful")
                    if opt_status.is_signup:
                        opt_status.is_active = False
                        opt_status.save()
                        return redirect('/login')
                    else:
                        # return redirect('/change-password')
                        return render(request, 'auth/resetpassword.html', {'email': email})
                else:
                    messages.error(request, "User not found")
            else:
                messages.error(request, 'Couldn`t verrify your otp')
    else:
        messages.error(request, 'something wrong')
    return render(request, 'auth/otp.html')


@login_required
def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    return redirect('frontpage')


@login_required
def change_quantity(request, product_id):
    action = request.GET.get('action', '')

    if action:
        quantity = 1

        if action == 'decrease':
            quantity = -1

        cart = Cart(request)
        cart.add(product_id, quantity, True)

    return redirect('cart_view')


@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart_view')


@login_required
def cart_view(request):
    try:
        cart = Cart(request)
        about = About.objects.all().first()
        categories = Category.objects.all()

        return render(request, 'store/cart_view.html', {
            'cart': cart,
            'about': about,
            'categories': categories,

        })
    except:
        pass


@login_required
def checkout(request, pk):
    try:
        cart = Cart(request)
        about = About.objects.all().first()
        categories = Category.objects.all()
        profile = CustomerProfile.objects.get(user_id=pk)

        if request.method == 'POST':
            form = OrderForm(request.POST)

            if form.is_valid():
                total_price = 0

                for item in cart:
                    product = item['product']
                    # print(product.price)
                    # print(int(item['quantity']))
                    total_price += product.price * int(item['quantity']) + 100

                # order = form.save(commit=False)
                # order.created_by = request.user
                # order.merchant_id = request.user.id
                # order.total_cost = total_price
                # order.paid_amount = total_price
                # order.save()

                for item in cart:
                    product = item['product']
                    quantity = int(item['quantity'])
                    price = product.price * quantity

                    item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity,
                                                    created_by_id=request.user.id)
                cart.clear()

            return redirect('frontpage')
        else:
            form = OrderForm()

        return render(request, 'store/checkout.html', {
            'cart': cart,
            'form': form,
            'about': about,
            'categories': categories,
            'profile': profile,

        })
    except Exception as e:
        print(e)
        return render(request, 'store/profile_form.html', )


def search(request):
    try:
        query = request.GET.get('query', '')
        products = Product.objects.filter(status=Product.ACTIVE).filter(
            Q(title__icontains=query) | Q(description__icontains=query))
        about = About.objects.all().first()
        categories = Category.objects.all()

        return render(request, 'store/search.html', {
            'query': query,
            'products': products,
            'about': about,
            'categories': categories,

        })
    except:
        pass


def category_detail(request, slug):
    try:
        category = get_object_or_404(Category, slug=slug)
        products = category.products.filter(status=Product.ACTIVE)
        about = About.objects.all().first()
        categories = Category.objects.all()

        return render(request, 'store/category_detail.html', {
            'category': category,
            'products': products,
            'about': about,
            'categories': categories,
        })
    except:
        pass


def product_detail(request, category_slug, slug):
    try:
        product = get_object_or_404(Product, slug=slug, status=Product.ACTIVE)
        categories = Category.objects.all()

        if request.method == 'POST':
            rating = request.POST.get('rating', 3)
            content = request.POST.get('content', '')
            print("rating", rating, "content", content)
            if content:
                review = Review.objects.create(
                    product=product,
                    rating=rating,
                    content=content,
                    created_by=request.user
                )
                # reviews = Review.objects.filter(created_by=request.user, product=product)
                # if reviews:
                #     review = reviews.first()
                #     review.rating = rating
                #     review.content = content
                #     review.save()
                # else:
                #     review = Review.objects.create(
                #         product=product,
                #         rating=rating,
                #         content=content,
                #         created_by=request.user
                #     )
        content = {}
        review = Review.objects.filter(product_id=product.id)
        random_products = Product.objects.filter(category_id=product.category.id, status='Active').order_by('-id')
        about = About.objects.all().first()
        try:
            print("==============")
            con_pid, coll_pid, hyb_pid = hybrid_recommendation(request, product.id)
            if not hyb_pid == None:
                content['recommended_products'] = Product.objects.filter(id__in=hyb_pid[1:6], status='Active')
            elif not coll_pid == None:
                content['recommended_products'] = Product.objects.filter(id__in=coll_pid[1:6], status='Active')
            else:
                content['recommended_products'] = Product.objects.filter(id__in=con_pid[1:6], status='Active')
        except:
            pass

        print("Outside After recommendation", content)
        return render(request, 'store/product_detail.html', {
            'product': product,
            'random_products': random_products,
            'reviews': review,
            'recommended_products': content['recommended_products'],
            'about': about,
            'categories': categories,

        })
    except Exception as e:
        print("Exception", e)


class ProductListView(ListView):
    template_name = "store/product_list.html"
    model = Product
    queryset = Product.objects.filter(status='Active')
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['about'] = About.objects.all().first()
            context['categories'] = Category.objects.all()
        except:
            pass
        return context


class AddProfileView(LoginRequiredMixin, CreateView):
    template_name = "store/profile_form.html"
    form_class = ProfileForm
    model = CustomerProfile
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['about'] = About.objects.all().first()
            context['categories'] = Category.objects.all()
        except:
            pass
        return context

    def form_invalid(self, form):
        return render(self.request, 'store/profile_form.html', {
            'form': form,
        })

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.id})


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = "store/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['about'] = About.objects.all().first()
            context['categories'] = Category.objects.all()
            context['profile'] = CustomerProfile.objects.get(user=self.request.user.id)
            context['order_items'] = OrderItem.objects.filter(created_by=self.request.user.id)
        except:
            pass
        return context

    def get_queryset(self):
        return EcommerceUser.objects.filter(id=self.kwargs.get('pk'))


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    template_name = "store/update_profile_form.html"
    fields = ['first_name', 'last_name', 'address', 'mobileNo', 'photo', 'user']
    model = CustomerProfile

    # context_object_name = 'con_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['about'] = About.objects.all().first()
            context['categories'] = Category.objects.all()
            context['profile'] = CustomerProfile.objects.get(user=self.request.user.id)
        except:
            pass
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        return CustomerProfile.objects.filter(id=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.id})


class ResetPasswordView(TemplateView):
    template_name = 'auth/forgetpassword.html'

    def post(self, form):
        email = self.request.POST.get('email')
        sendOTPToUserForForgotPassword(email=email)
        messages.success(self.request, 'Please verify your otp')
        return redirect('/otp-verify?value={}'.format(email))


class ChangePasswordView(TemplateView):
    template_name = 'auth/resetpassword.html'

    def post(self, form):
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        confirmpassword = self.request.POST.get('confirm_password')
        if password != confirmpassword:
            messages.warning(self.request, "Password is Incorrect")
            return render(self.request, 'auth/forgetpassword.html')
        else:
            print("password", password)
            print("hashed password", make_password(password))
            user = EcommerceUser.objects.get(email=email)
            user.password = make_password(password)
            user.save()
        return redirect('/login')


@csrf_exempt
def verify_payment(request):
    try:
        print("start")
        data = request.POST
        print(data)
        # product_id = data['product_identity']
        token = data['token']
        amount = data['total_amount']
        first_name = data['first_name']
        last_name = data['last_name']
        address = data['address']
        mobile_no = data['mobile_no']
        zipcode = data['zip_code']
        city = data['city']
        user_id = data['user_id']

        print("khalti data :", token)
        print("site data :", amount, first_name, last_name, address, mobile_no, zipcode, city, user_id)
        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "Key test_secret_key_3e92a0534adb416c89518776e306ebc4"
        }

        # response = request.post(url, payload, headers=headers)
        # print("=============", response)
        #
        # response_data = json.loads(response.text)
        # status_code = str(response.status_code)
        #
        # if status_code == '400':
        #     response = JsonResponse({'status': 'false', 'message': response_data['detail']}, status=500)
        #     return response

        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(response_data)
        amount = float(amount) / 100
        order = Order(first_name=first_name, last_name=last_name, address=address, zipcode=zipcode, city=city,
                      mobile_no=mobile_no, total_cost=amount, paid_amount=amount, merchant_id=user_id,
                      created_by_id=user_id, is_paid=True)
        order.save()
        cart = Cart(request)
        about = About.objects.all().first()
        categories = Category.objects.all()
        profile = CustomerProfile.objects.get(user_id=user_id)
        for item in cart:
            product = item['product']
            quantity = int(item['quantity'])
            price = product.price * quantity

            item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity,
                                            created_by_id=request.user.id)
        cart.clear()
        print("verified payment")

        return render(request, 'store/product_list.html', {
            'cart': cart,
            'about': about,
            'categories': categories,
            'profile': profile,
            'products': Product.objects.filter(status='Active')

        })  # return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}", safe=False)

    except Exception as e:
        print("Verification not success", e)
