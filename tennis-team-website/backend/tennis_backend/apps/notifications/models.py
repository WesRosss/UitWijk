"""
Notification models for Tennis Team Website.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from tennis_backend.apps.users.models import CustomUser
from tennis_backend.settings.base import NOTIFICATION_TYPES


class NotificationPreference(models.Model):
    """
    Model to store user notification preferences.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('User'),
        help_text=_('The user who owns these preferences.')
    )
    
    notification_type = models.CharField(
        _('Notification Type'),
        max_length=50,
        choices=NOTIFICATION_TYPES,
        help_text=_('The type of notification.')
    )
    
    email_notification = models.BooleanField(
        _('Email Notification'),
        default=True,
        help_text=_('Whether to send email notifications for this type.')
    )
    
    in_app_notification = models.BooleanField(
        _('In-App Notification'),
        default=True,
        help_text=_('Whether to show in-app notifications for this type.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
        unique_together = ['user', 'notification_type']
        ordering = ['user__username', 'notification_type']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"
    
    def get_notification_type_display(self):
        """Get display name for notification type."""
        return dict(NOTIFICATION_TYPES).get(self.notification_type, self.notification_type)
    
    def should_send_email(self):
        """Check if email notification should be sent."""
        return self.email_notification
    
    def should_show_in_app(self):
        """Check if in-app notification should be shown."""
        return self.in_app_notification


class Notification(models.Model):
    """
    Model to store notifications for users.
    """
    # Notification types
    MATCH_CREATED = 'match_created'
    MATCH_UPDATED = 'match_updated'
    MATCH_CANCELLED = 'match_cancelled'
    ASSIGNMENT_CREATED = 'assignment_created'
    ASSIGNMENT_UPDATED = 'assignment_updated'
    AVAILABILITY_REQUEST = 'availability_request'
    RESPONSIBILITY_ASSIGNED = 'responsibility_assigned'
    TEAM_ANNOUNCEMENT = 'team_announcement'
    
    # Notification status
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    READ = 'read'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
        (FAILED, 'Failed'),
        (READ, 'Read'),
    ]
    
    # Notification delivery types
    EMAIL = 'email'
    IN_APP = 'in_app'
    BOTH = 'both'
    
    DELIVERY_CHOICES = [
        (EMAIL, 'Email'),
        (IN_APP, 'In-App'),
        (BOTH, 'Both'),
    ]
    
    # Related models
    RELATED_MODELS = [
        ('match', 'Match'),
        ('team', 'Team'),
        ('player', 'Player'),
        ('availability', 'Availability'),
        ('assignment', 'Assignment'),
        ('responsibility', 'Responsibility'),
        ('user', 'User'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User'),
        help_text=_('The user who should receive this notification.')
    )
    
    title = models.CharField(
        _('Title'),
        max_length=255,
        help_text=_('The title of the notification.')
    )
    
    message = models.TextField(
        _('Message'),
        help_text=_('The content of the notification.')
    )
    
    notification_type = models.CharField(
        _('Notification Type'),
        max_length=50,
        choices=NOTIFICATION_TYPES,
        help_text=_('The type of notification.')
    )
    
    delivery_type = models.CharField(
        _('Delivery Type'),
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=IN_APP,
        help_text=_('How this notification should be delivered.')
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text=_('The current status of the notification.')
    )
    
    related_model = models.CharField(
        _('Related Model'),
        max_length=50,
        choices=RELATED_MODELS,
        help_text=_('The model this notification is related to.')
    )
    
    related_id = models.PositiveIntegerField(
        _('Related ID'),
        help_text=_('The ID of the related object.')
    )
    
    is_read = models.BooleanField(
        _('Is Read'),
        default=False,
        help_text=_('Whether the user has read this notification.')
    )
    
    read_at = models.DateTimeField(
        _('Read At'),
        null=True,
        blank=True,
        help_text=_('When the user read this notification.')
    )
    
    # For scheduled notifications (hourly bundling)
    scheduled_for = models.DateTimeField(
        _('Scheduled For'),
        null=True,
        blank=True,
        help_text=_('When this notification should be sent (for bundled notifications).')
    )
    
    sent_at = models.DateTimeField(
        _('Sent At'),
        null=True,
        blank=True,
        help_text=_('When this notification was sent.')
    )
    
    # For email notifications
    email_subject = models.CharField(
        _('Email Subject'),
        max_length=255,
        blank=True,
        help_text=_('The subject line for email notifications.')
    )
    
    email_sent = models.BooleanField(
        _('Email Sent'),
        default=False,
        help_text=_('Whether the email has been sent.')
    )
    
    email_sent_at = models.DateTimeField(
        _('Email Sent At'),
        null=True,
        blank=True,
        help_text=_('When the email was sent.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_read']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} for {self.user.username}"
    
    def get_notification_type_display(self):
        """Get display name for notification type."""
        return dict(NOTIFICATION_TYPES).get(self.notification_type, self.notification_type)
    
    def get_status_display(self):
        """Get display name for status."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_delivery_type_display(self):
        """Get display name for delivery type."""
        return dict(self.DELIVERY_CHOICES).get(self.delivery_type, self.delivery_type)
    
    def mark_as_read(self):
        """Mark this notification as read."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self):
        """Mark this notification as sent."""
        self.status = self.SENT
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark this notification as failed."""
        self.status = self.FAILED
        self.save()
    
    def mark_email_sent(self):
        """Mark the email as sent."""
        self.email_sent = True
        self.email_sent_at = timezone.now()
        self.save()
    
    def should_send_email(self):
        """Check if email should be sent for this notification."""
        if self.delivery_type in [self.EMAIL, self.BOTH]:
            # Check user preferences
            try:
                pref = NotificationPreference.objects.get(
                    user=self.user,
                    notification_type=self.notification_type
                )
                return pref.should_send_email()
            except NotificationPreference.DoesNotExist:
                return True  # Default to sending email if no preference
        return False
    
    def should_show_in_app(self):
        """Check if in-app notification should be shown."""
        if self.delivery_type in [self.IN_APP, self.BOTH]:
            # Check user preferences
            try:
                pref = NotificationPreference.objects.get(
                    user=self.user,
                    notification_type=self.notification_type
                )
                return pref.should_show_in_app()
            except NotificationPreference.DoesNotExist:
                return True  # Default to showing in-app if no preference
        return False


class NotificationBatch(models.Model):
    """
    Model to track batches of notifications for hourly bundling.
    """
    batch_identifier = models.CharField(
        _('Batch Identifier'),
        max_length=64,
        unique=True,
        help_text=_('A unique identifier for this batch.')
    )
    
    notification_type = models.CharField(
        _('Notification Type'),
        max_length=50,
        blank=True,
        help_text=_('The type of notifications in this batch (optional).')
    )
    
    scheduled_time = models.DateTimeField(
        _('Scheduled Time'),
        help_text=_('When this batch should be processed.')
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('The current status of this batch.')
    )
    
    total_notifications = models.PositiveIntegerField(
        _('Total Notifications'),
        default=0,
        help_text=_('The total number of notifications in this batch.')
    )
    
    processed_notifications = models.PositiveIntegerField(
        _('Processed Notifications'),
        default=0,
        help_text=_('The number of notifications that have been processed.')
    )
    
    started_at = models.DateTimeField(
        _('Started At'),
        null=True,
        blank=True,
        help_text=_('When processing of this batch started.')
    )
    
    completed_at = models.DateTimeField(
        _('Completed At'),
        null=True,
        blank=True,
        help_text=_('When processing of this batch was completed.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Batch')
        verbose_name_plural = _('Notification Batches')
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['batch_identifier']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Batch {self.batch_identifier} - {self.get_status_display()}"
    
    def get_status_display(self):
        """Get display name for status."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def mark_as_processing(self):
        """Mark this batch as processing."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()
    
    def mark_as_completed(self):
        """Mark this batch as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark this batch as failed."""
        self.status = 'failed'
        self.save()
    
    def increment_processed(self):
        """Increment the processed notifications count."""
        self.processed_notifications += 1
        self.save()
    
    def is_ready_to_process(self):
        """Check if this batch is ready to be processed."""
        return self.status == 'pending' and self.scheduled_time <= timezone.now()
    
    def get_progress_percentage(self):
        """Get the progress percentage."""
        if self.total_notifications == 0:
            return 0
        return (self.processed_notifications / self.total_notifications) * 100