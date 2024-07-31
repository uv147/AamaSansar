from django.db import models
from django.core.files import File

from io import BytesIO
from PIL import Image
from django.utils.text import slugify

from vendor.models import EcommerceUser

ORDER_TRACKING_CHOICE = (
    ("Order Requested", 'Order Requested'),
    ("Packaging", 'Packaging'),
    ("On The Way", 'On The Way'),
    ("Delivered", 'Delivered')

)


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    DRAFT = 'Draft'
    WAITING_APPROVAL = 'Waitingapproval'
    ACTIVE = 'Active'
    DELETED = 'Deleted'

    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (WAITING_APPROVAL, 'Waiting approval'),
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted')

    )
    user = models.ForeignKey(EcommerceUser, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='uploads/product_images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/product_images/thumbnail/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=ACTIVE)

    class Meta:
        ordering = ('-price',)

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return 'https://via.placeholder.com/240x240x.jpg'

    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        name = image.name.replace('uploads/product_images/', '')
        thumbnail = File(thumb_io, name=name)
        return thumbnail

    def get_rating(self):
        reviews_total = 0
        for review in self.reviews.all():
            reviews_total += review.rating

        if reviews_total > 0:
            return reviews_total / self.reviews.count()

        return 0


class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=10, blank=True, null=True)
    total_cost = models.IntegerField(default=0)
    paid_amount = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    merchant_id = created_by = models.CharField(max_length=255)
    created_by = models.ForeignKey(EcommerceUser, related_name='orders', on_delete=models.SET_NULL, null=True)


class OrderItem(models.Model):
    # ORDER_REQUESTED = 'Order Requested'
    # PACKAGING = 'Packaging'
    # ON_THE_WAY = 'On The Way'
    # DELIVERED = 'Delivered'

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    tracking_status = models.CharField(max_length=50, choices=ORDER_TRACKING_CHOICE, default="Order Requested")
    created_by = models.ForeignKey(EcommerceUser, related_name='ordered_item', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews_product', on_delete=models.CASCADE)
    rating = models.IntegerField(default=3)
    content = models.TextField()
    created_by = models.ForeignKey(EcommerceUser, related_name='reviews_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CustomerProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    mobileNo = models.CharField(max_length=10)
    photo = models.ImageField(blank=True, null=True, upload_to='Customer Profile')
    user = models.ForeignKey(EcommerceUser, related_name="customer_detail", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(blank=True, auto_now=True)


class UserOTP(models.Model):
    email = models.TextField(null=True)
    otp = models.IntegerField(null=True)
    is_signup = models.BooleanField(default=False)
    is_forgot_password = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
