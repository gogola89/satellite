from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import MyAccountManager


class Account(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=50, unique=False)
    profile_picture = models.ImageField(
        upload_to='userprofile', blank=True, null=True)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name', 'phone_number', 'country']

    objects = MyAccountManager()

    @property
    def profileURL(self):
        try:
            url = self.profile_picture.url
        except:
            url = '/images/avatars/default.png'
        return url

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_perms(self, perms, obj=None):
        return self.is_superuser

    def has_module_perms(self, add_label):
        return True

    def __str__(self):
        return self.email
