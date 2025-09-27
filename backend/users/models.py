from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers.UserManager import UserManager
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    objects = UserManager()
    USER_ROLES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('publisher', 'Publisher'),
        ('guest', 'Guest')
    ]
    
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')

    #Sitie changes reikalinga, norint loginint su email ir password o ne username password
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
