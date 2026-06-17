"""
User models for Tennis Team Website.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from tennis_backend.settings.base import USER_ROLES


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with role-based access control.
    """
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    objects = CustomUserManager()
    
    # User roles
    ADMIN = 'admin'
    COORDINATOR = 'coordinator'
    PLAYER = 'player'
    
    ROLE_CHOICES = USER_ROLES
    
    # Basic user information
    username = models.CharField(
        _('Username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    
    email = models.EmailField(
        _('Email Address'),
        unique=True,
        help_text=_('Required. Must be a valid email address.')
    )
    
    first_name = models.CharField(_('First Name'), max_length=150)
    last_name = models.CharField(_('Last Name'), max_length=150)
    
    # Contact information
    phone = models.CharField(
        _('Phone Number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Optional phone number for contact.')
    )
    
    # Role-based access control
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=PLAYER,
        help_text=_('User role determines permissions.')
    )
    
    # User status
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    
    is_staff = models.BooleanField(
        _('Staff Status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.')
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    last_login = models.DateTimeField(_('Last Login'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def get_role_display(self):
        """Return the display name for the user's role."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.ADMIN or self.is_superuser
    
    def is_coordinator(self):
        """Check if user is a coordinator."""
        return self.role == self.COORDINATOR or self.is_admin()
    
    def is_player(self):
        """Check if user is a player."""
        return self.role == self.PLAYER
    
    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission."""
        # Admin users have all permissions
        if self.is_admin():
            return True
        
        # Coordinator users have specific permissions
        if self.is_coordinator():
            coordinator_permissions = [
                'view_user', 'view_team', 'view_match', 'view_player',
                'add_match', 'change_match', 'delete_match',
                'add_player', 'change_player',
                'add_assignment', 'change_assignment', 'delete_assignment',
                'add_responsibility', 'change_responsibility', 'delete_responsibility',
                'view_notification', 'add_notification',
            ]
            if perm in coordinator_permissions:
                return True
        
        # Default permission checking
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """Check if user has permissions for a module."""
        if self.is_admin():
            return True
        if self.is_coordinator() and app_label in ['users', 'teams', 'matches', 'notifications']:
            return True
        return super().has_module_perms(app_label)


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    
    # Profile picture
    profile_picture = models.ImageField(
        _('Profile Picture'),
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Date of birth
    date_of_birth = models.DateField(
        _('Date of Birth'),
        blank=True,
        null=True
    )
    
    # Address information
    address = models.TextField(_('Address'), blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State/Province'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True, default='Netherlands')
    
    # Emergency contact
    emergency_contact_name = models.CharField(
        _('Emergency Contact Name'),
        max_length=150,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        _('Emergency Contact Phone'),
        max_length=20,
        blank=True
    )
    emergency_contact_relationship = models.CharField(
        _('Emergency Contact Relationship'),
        max_length=50,
        blank=True
    )
    
    # Medical information (optional)
    medical_notes = models.TextField(_('Medical Notes'), blank=True)
    allergies = models.TextField(_('Allergies'), blank=True)
    
    # Preferences
    preferred_contact_method = models.CharField(
        _('Preferred Contact Method'),
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('both', 'Both'),
        ],
        default='email'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"
    
    def get_age(self):
        """Calculate user's age based on date of birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None