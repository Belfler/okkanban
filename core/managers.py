from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    CustomUser model manager where email is the unique identifier for authentication instead of username.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a CustomUser with the given email and password.
        """
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self.create_user(email, password, **extra_fields)
