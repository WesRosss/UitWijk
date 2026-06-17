"""
Custom user managers for Tennis Team Website.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager with email as the unique identifier.
    """
    
    def create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email and password.
        """
        if not username:
            raise ValueError(_('The username must be set'))
        if not email:
            raise ValueError(_('The email must be set'))
        
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and save a superuser with the given username, email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        """
        Get user by natural key (username).
        """
        return self.get(username=username)
    
    def get_admins(self):
        """
        Get all admin users.
        """
        return self.filter(models.Q(role='admin') | models.Q(is_superuser=True))
    
    def get_coordinators(self):
        """
        Get all coordinator users.
        """
        return self.filter(role='coordinator')
    
    def get_players(self):
        """
        Get all player users.
        """
        return self.filter(role='player')
    
    def get_active_users(self):
        """
        Get all active users.
        """
        return self.filter(is_active=True)


# Import models for use in manager methods
from django.db import models
from .models import CustomUser
CustomUserManager.models = CustomUser