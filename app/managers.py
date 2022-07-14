from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):
    def create_user(self, full_name, email, phone_number, country, password=None):
        if not email:
            raise ValueError(_("User must have an email"))

        if not phone_number:
            raise ValueError(_("User must have phone number"))

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone_number=phone_number,
            country=country,
        )

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_superuser(self, full_name, email, phone_number, country, password):
        user = self.create_user(
            email=self.normalize_email(email),
            full_name=full_name,
            phone_number=phone_number,
            country=country,
            password=password,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user
