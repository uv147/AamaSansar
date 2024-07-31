from django.db import models
from django.utils.text import slugify


# Create your models here.
class Banner(models.Model):
    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=500)
    image = models.ImageField(upload_to="Banner")
    weight = models.IntegerField()
    published = models.BooleanField(default=True)


class About(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    logo = models.ImageField(blank=True, null=True, upload_to="AboutUs")
    photo = models.ImageField(blank=True, null=True, upload_to="AboutUs")
    phoneNo = models.CharField(max_length=9)
    mobileNo = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=100)
    slug = models.SlugField()

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super(About, self).save(*args, **kwargs)

