from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser without the username field.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    user_type = models.CharField(
        max_length=10,
        choices=[('guest', 'Guest'), ('employee', 'Employee')],
        default='guest'
    )
    primary_phone = models.CharField(max_length=15, unique=True)
    secondary_phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['full_name', 'primary_phone']  # Fields required when creating a user

    objects = CustomUserManager()  # Attach the custom manager

    def __str__(self):
        return self.full_name


class Request(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('on process', 'On Process'),
        ('closed', 'Closed'),
    )

    TYPE_CHOICES = (
        ('new', 'New'),
        ('complain', 'Complain'),
    )

    employee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='employee_requests')
    guest = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='guest_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    last_date_time = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=500 , null=True, default=None)
    notes = models.TextField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"Request from guest : {self.guest.full_name} to employee : {self.employee.full_name if self.guest else 'Unknown'}"
