import datetime

from django.db import models

# Create your models here.
import uuid
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
import hashlib
from .managers import CustomUserManager
from .utils import get_masked_pan, hash_pan
import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
# Create your models here.

class UserType(models.Model): #partner type
    name = models.CharField(max_length=40, unique=True)
    display = models.CharField(max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class Industry(models.Model):
    name = models.CharField(max_length=40, unique=True)
    display = models.CharField(max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class CompanyType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    display = models.CharField(max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Verification(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    otp = models.CharField(max_length=6)
    expiration = models.DateTimeField()

    def is_otp_valid(self):
        return self.expiration > timezone.now()

    def clean(self):
        super().clean()
        if not self.is_valid_identifier():
            raise ValidationError("Invalid identifier format")

    def is_valid_identifier(self):
        # Check if the identifier is a valid email or phone number
        if re.match(r"[^@]+@[^@]+\.[^@]+", self.identifier):  # Check for a valid email
            return True
        elif re.match(r"\d{10,15}", self.identifier):  # Check for a valid phone number
            return True
        return False




class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          serialize=False, verbose_name='ID')
    email = models.CharField(default='', null=True, blank=True, max_length=200)
    pan_number = models.CharField(max_length=300, unique=True)
    is_company = models.BooleanField(default=False)
    masked_pan = models.CharField(max_length=10,  blank=True, null=True)
    incorporation_date = models.DateField(blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(CompanyType, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200, blank=False, null=False)
    city = models.CharField(max_length=100, default="", null=True, blank=True)
    state = models.CharField(max_length=100, default="", null=True, blank=True)
    district = models.CharField(max_length=100, default="", null=True, blank=True)
    country = models.CharField(max_length=100, default="India", null=True, blank=True)
    cin = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, default='', null=True, blank=True)

    def save(self, *args, **kwargs):

        self.masked_pan = self.masked_pan if len(self.pan_number) > 10 else get_masked_pan(self.pan_number)  # Set masked_pan value
        self.pan_number = self.pan_number if len(self.pan_number) > 10 else hash_pan(self.pan_number)  # Hash the PAN number
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     self.masked_pan, self.pan_number = mask_and_hash_pan(self.pan_number)
    #     super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    """
    Model to store all kinds of users in the database.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          serialize=False, verbose_name='ID')
    email = models.CharField(_('email address'), null=True,blank=True, max_length=200)
    pan_number = models.CharField(max_length=300, unique=True)
    masked_pan = models.CharField(max_length=10, blank=True, null=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, blank=True, null=True)
    business =  models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=200,  blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(_('is active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_premium_user = models.BooleanField(default=False)
    created_by = models.ForeignKey('self',  on_delete=models.CASCADE, blank=True, null=True)
    objects = CustomUserManager()
    is_mobile_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'pan_number'
    REQUIRED_FIELDS = []
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # unique_together = ('phone_number', 'pan_number','email')

    def save(self, *args, **kwargs):
            # self.masked_pan = get_masked_pan(self.pan_number)
            # self.pan_number = hash_pan(self.pan_number)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.pan_number

