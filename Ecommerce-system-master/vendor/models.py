from django.contrib.auth.models import AbstractUser
from django.db import models


class EcommerceUser(AbstractUser):
    is_vendor = models.BooleanField(default=False)
    is_OTP_verified = models.BooleanField(default=False)


class VendorDetail(models.Model):
    company_name = models.CharField(max_length=150)
    company_address = models.CharField(max_length=100)
    company_phone = models.PositiveBigIntegerField()
    pan_vat_no = models.PositiveBigIntegerField()
    company_registered_document = models.ImageField(blank=True, null=True, upload_to='Registered Company')
    pan_vat_registered_document = models.ImageField(upload_to='Pan Vat Registered')
    vendor = models.ForeignKey(EcommerceUser, related_name="vendor_detail", on_delete=models.CASCADE)
    verify_status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(EcommerceUser, related_name="vendor_detail_modified", on_delete=models.SET_NULL,
                                    blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, auto_now=True)
