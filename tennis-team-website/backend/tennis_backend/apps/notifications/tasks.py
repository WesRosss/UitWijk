"""
Celery tasks for the notification system.
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from .models import Notification, NotificationBatch, NotificationPreference
from tennis_backend.apps.users.models import CustomUser
from tennis_backend.apps.matches.models import Match, PlayerAvailability, MatchAssignment
from tennis_backend.apps.teams.models import Team, Player
import uuid

logger = logging.getLogger(__name__)


@shared_task
def send_hourly_notifications():
    """
    Send bundled notifications hourly.
    This task runs every hour and sends all pending notifications.
    """
    logger.info("Starting hourly notification processing...")
    
    try:
        # Get all pending notifications that should be sent now
        now = timezone.now()
        
        # Find notifications that are scheduled for this hour or earlier
        notifications_to_send = Notification.objects.filter(
            status=Notification.PENDING,
            scheduled_for__lte=now
        ).select_related('user')
        
        if not notifications_to_send.exists():
            logger.info("No pending notifications to send.")
            return {
                'status': 'success',
                'notifications_processed': 0,
                'emails_sent': 0,
                'in_app_notifications': 0
            }
        
        # Create a batch for this run
        batch_identifier = f"hourly-{now.strftime('%Y%m%d-%H')}-{uuid.uuid4().hex[:8]}"
        batch = NotificationBatch.objects.create(
            batch_identifier=batch_identifier,
            notification_type='hourly_bundle',
            scheduled_time=now,
            status='processing',
            total_notifications=notifications_to_send.count()
        )
        
        emails_sent = 0
        in_app_notifications = 0
        failed_notifications = 0
        
        # Group notifications by user
        notifications_by_user = {}
        for notification in notifications_to_send:
            user_id = notification.user_id
            if user_id not in notifications_by_user:
                notifications_by_user[user_id] = []
            notifications_by_user[user_id].append(notification)
        
        # Process each user's notifications
        for user_id, user_notifications in notifications_by_user.items():
            try:
                user = CustomUser.objects.get(id=user_id)
                
                # Get user's notification preferences
                preferences = NotificationPreference.objects.filter(user=user).values_list(
                    'notification_type', 'email_notification', 'in_app_notification'
                )
                pref_dict = {pref[0]: {'email': pref[1], 'in_app': pref[2]} for pref in preferences}
                
                # Separate notifications by delivery type
                email_notifications = []
                in_app_notifications_list = []
                
                for notification in user_notifications:
                    # Check if this notification type should be sent via email
                    notification_pref = pref_dict.get(notification.notification_type, {})
                    should_send_email = notification_pref.get('email', True)
                    should_show_in_app = notification_pref.get('in_app', True)
                    
                    if notification.delivery_type in ['email', 'both'] and should_send_email:
                        email_notifications.append(notification)
                    
                    if notification.delivery_type in ['in_app', 'both'] and should_show_in_app:
                        in_app_notifications_list.append(notification)
                
                # Send email if there are email notifications
                if email_notifications:
                    email_sent = send_user_notification_email(user, email_notifications)
                    if email_sent:
                        emails_sent += 1
                        # Mark email notifications as sent
                        for notification in email_notifications:
                            notification.email_sent = True
                            notification.email_sent_at = now
                            notification.save()
                    else:
                        failed_notifications += len(email_notifications)
                
                # Mark in-app notifications as sent
                if in_app_notifications_list:
                    for notification in in_app_notifications_list:
                        notification.status = Notification.SENT
                        notification.sent_at = now
                        notification.save()
                        in_app_notifications += 1
                
                # Mark all notifications as processed
                for notification in user_notifications:
                    if notification.status == Notification.PENDING:
                        notification.status = Notification.SENT
                        notification.sent_at = now
                        notification.save()
                
                batch.processed_notifications += len(user_notifications)
                
            except CustomUser.DoesNotExist:
                logger.warning(f"User {user_id} not found, skipping notifications.")
                # Mark these notifications as failed
                for notification in user_notifications:
                    notification.status = Notification.FAILED
                    notification.save()
                failed_notifications += len(user_notifications)
                batch.processed_notifications += len(user_notifications)
            except Exception as e:
                logger.error(f"Error processing notifications for user {user_id}: {str(e)}")
                # Mark these notifications as failed
                for notification in user_notifications:
                    notification.status = Notification.FAILED
                    notification.save()
                failed_notifications += len(user_notifications)
                batch.processed_notifications += len(user_notifications)
        
        # Mark batch as completed
        batch.mark_as_completed()
        
        logger.info(
            f"Hourly notification processing completed. "
            f"Processed: {batch.processed_notifications}, "
            f"Emails sent: {emails_sent}, "
            f"In-app: {in_app_notifications}, "
            f"Failed: {failed_notifications}"
        )
        
        return {
            'status': 'success',
            'batch_id': batch.id,
            'notifications_processed': batch.processed_notifications,
            'emails_sent': emails_sent,
            'in_app_notifications': in_app_notifications,
            'failed_notifications': failed_notifications
        }
        
    except Exception as e:
        logger.error(f"Error in send_hourly_notifications: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'notifications_processed': 0,
            'emails_sent': 0,
            'in_app_notifications': 0
        }


@shared_task
def send_user_notification_email(user, notifications):
    """
    Send an email with bundled notifications to a user.
    """
    try:
        # Group notifications by type for better organization
        notifications_by_type = {}
        for notification in notifications:
            notification_type = notification.notification_type
            if notification_type not in notifications_by_type:
                notifications_by_type[notification_type] = []
            notifications_by_type[notification_type].append(notification)
        
        # Render email template
        subject = f"Tennis Team: {len(notifications)} New Notifications"
        
        context = {
            'user': user,
            'notifications': notifications,
            'notifications_by_type': notifications_by_type,
            'site_name': getattr(settings, 'SITE_NAME', 'Tennis Team Website'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8080'),
        }
        
        # Try to render HTML email
        try:
            html_message = render_to_string('emails/notifications_bundle.html', context)
        except Exception:
            html_message = None
        
        # Try to render text email
        try:
            text_message = render_to_string('emails/notifications_bundle.txt', context)
        except Exception:
            text_message = f"You have {len(notifications)} new notifications. Please visit the website to view them."
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending notification email to {user.email}: {str(e)}")
        return False


@shared_task
def cleanup_old_notifications():
    """
    Clean up old notifications (older than 30 days).
    """
    logger.info("Starting notification cleanup...")
    
    try:
        # Delete notifications older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=thirty_days_ago
        ).delete()
        
        logger.info(f"Deleted {deleted_count} old notifications.")
        
        return {
            'status': 'success',
            'notifications_deleted': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_notifications: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'notifications_deleted': 0
        }


@shared_task
def create_match_notifications(match_id, action='created'):
    """
    Create notifications for match-related actions.
    """
    try:
        match = Match.objects.get(id=match_id)
        
        if action == 'created':
            # Notify all players in the home team
            if match.home_team:
                for player in match.home_team.players.all():
                    if player.user.is_active:
                        create_notification_for_user(
                            user=player.user,
                            notification_type='match_created',
                            title=f"New Match: {match.get_team_names()}",
                            message=f"A new match has been scheduled for {match.match_date} at {match.start_time}.",
                            related_model='match',
                            related_id=match.id,
                            delivery_type='both'
                        )
            
            # Notify all players in the away team
            if match.away_team:
                for player in match.away_team.players.all():
                    if player.user.is_active:
                        create_notification_for_user(
                            user=player.user,
                            notification_type='match_created',
                            title=f"New Match: {match.get_team_names()}",
                            message=f"A new match has been scheduled for {match.match_date} at {match.start_time}.",
                            related_model='match',
                            related_id=match.id,
                            delivery_type='both'
                        )
        
        elif action == 'updated':
            # Notify all assigned players
            for assignment in match.assignments.all():
                if assignment.player.user.is_active:
                    create_notification_for_user(
                        user=assignment.player.user,
                        notification_type='match_updated',
                        title=f"Match Updated: {match.get_team_names()}",
                        message=f"The match scheduled for {match.match_date} has been updated.",
                        related_model='match',
                        related_id=match.id,
                        delivery_type='both'
                    )
        
        elif action == 'cancelled':
            # Notify all assigned players
            for assignment in match.assignments.all():
                if assignment.player.user.is_active:
                    create_notification_for_user(
                        user=assignment.player.user,
                        notification_type='match_cancelled',
                        title=f"Match Cancelled: {match.get_team_names()}",
                        message=f"The match scheduled for {match.match_date} has been cancelled.",
                        related_model='match',
                        related_id=match.id,
                        delivery_type='both'
                    )
        
        return {
            'status': 'success',
            'match_id': match_id,
            'action': action
        }
        
    except Match.DoesNotExist:
        logger.error(f"Match {match_id} not found for notification creation.")
        return {
            'status': 'error',
            'error': f'Match {match_id} not found'
        }
    except Exception as e:
        logger.error(f"Error creating match notifications: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def create_assignment_notifications(assignment_id, action='created'):
    """
    Create notifications for assignment-related actions.
    """
    try:
        from tennis_backend.apps.matches.models import MatchAssignment
        
        assignment = MatchAssignment.objects.get(id=assignment_id)
        
        if action == 'created':
            # Notify the assigned player
            create_notification_for_user(
                user=assignment.player.user,
                notification_type='assignment_created',
                title=f"New Assignment: {assignment.match}",
                message=f"You have been assigned to {assignment.match} as {assignment.position}.",
                related_model='assignment',
                related_id=assignment.id,
                delivery_type='both'
            )
            
            # Notify the person who made the assignment
            if assignment.assigned_by:
                create_notification_for_user(
                    user=assignment.assigned_by,
                    notification_type='assignment_created',
                    title=f"Assignment Created: {assignment.player.get_full_name()}",
                    message=f"You assigned {assignment.player.get_full_name()} to {assignment.match}.",
                    related_model='assignment',
                    related_id=assignment.id,
                    delivery_type='in_app'
                )
        
        elif action == 'updated':
            # Notify the assigned player
            create_notification_for_user(
                user=assignment.player.user,
                notification_type='assignment_updated',
                title=f"Assignment Updated: {assignment.match}",
                message=f"Your assignment for {assignment.match} has been updated.",
                related_model='assignment',
                related_id=assignment.id,
                delivery_type='both'
            )
        
        return {
            'status': 'success',
            'assignment_id': assignment_id,
            'action': action
        }
        
    except MatchAssignment.DoesNotExist:
        logger.error(f"Assignment {assignment_id} not found for notification creation.")
        return {
            'status': 'error',
            'error': f'Assignment {assignment_id} not found'
        }
    except Exception as e:
        logger.error(f"Error creating assignment notifications: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def create_availability_notification(availability_id):
    """
    Create notification when a player updates their availability.
    """
    try:
        availability = PlayerAvailability.objects.get(id=availability_id)
        
        # Notify coordinators about the availability update
        coordinators = CustomUser.objects.filter(
            role__in=['admin', 'coordinator'],
            is_active=True
        )
        
        for coordinator in coordinators:
            create_notification_for_user(
                user=coordinator,
                notification_type='availability_request',
                title=f"Availability Update: {availability.player.get_full_name()}",
                message=f"{availability.player.get_full_name()} has updated their availability for {availability.match} to {availability.get_status_display()}.",
                related_model='availability',
                related_id=availability.id,
                delivery_type='in_app'
            )
        
        return {
            'status': 'success',
            'availability_id': availability_id
        }
        
    except PlayerAvailability.DoesNotExist:
        logger.error(f"Availability {availability_id} not found for notification creation.")
        return {
            'status': 'error',
            'error': f'Availability {availability_id} not found'
        }
    except Exception as e:
        logger.error(f"Error creating availability notification: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def create_responsibility_notification(responsibility_id):
    """
    Create notification when a responsibility is assigned.
    """
    try:
        from tennis_backend.apps.matches.models import Responsibility
        
        responsibility = Responsibility.objects.get(id=responsibility_id)
        
        # Notify the assigned user
        create_notification_for_user(
            user=responsibility.user,
            notification_type='responsibility_assigned',
            title=f"New Responsibility: {responsibility.get_responsibility_type_display()}",
            message=f"You have been assigned to {responsibility.get_responsibility_type_display()} for {responsibility.match}.",
            related_model='responsibility',
            related_id=responsibility.id,
            delivery_type='both'
        )
        
        # Notify the person who made the assignment
        if responsibility.assigned_by:
            create_notification_for_user(
                user=responsibility.assigned_by,
                notification_type='responsibility_assigned',
                title=f"Responsibility Assigned: {responsibility.user.get_full_name()}",
                message=f"You assigned {responsibility.user.get_full_name()} to {responsibility.get_responsibility_type_display()} for {responsibility.match}.",
                related_model='responsibility',
                related_id=responsibility.id,
                delivery_type='in_app'
            )
        
        return {
            'status': 'success',
            'responsibility_id': responsibility_id
        }
        
    except Responsibility.DoesNotExist:
        logger.error(f"Responsibility {responsibility_id} not found for notification creation.")
        return {
            'status': 'error',
            'error': f'Responsibility {responsibility_id} not found'
        }
    except Exception as e:
        logger.error(f"Error creating responsibility notification: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


def create_notification_for_user(user, notification_type, title, message, 
                                 related_model, related_id, delivery_type='in_app',
                                 email_subject=None, scheduled_for=None):
    """
    Helper function to create a notification for a user.
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            delivery_type=delivery_type,
            related_model=related_model,
            related_id=related_id,
            email_subject=email_subject or title,
            scheduled_for=scheduled_for or timezone.now(),
            status=Notification.PENDING
        )
        
        logger.debug(f"Created notification {notification.id} for user {user.username}")
        return notification
        
    except Exception as e:
        logger.error(f"Error creating notification for user {user.username}: {str(e)}")
        return None