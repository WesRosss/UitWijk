"""
Team models for Tennis Team Website.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from tennis_backend.apps.users.models import CustomUser


class Team(models.Model):
    """
    Team model representing a tennis team.
    """
    name = models.CharField(
        _('Team Name'),
        max_length=100,
        unique=True,
        help_text=_('The name of the team.')
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('A description of the team.')
    )
    
    # Team coach (optional)
    coach = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coached_teams',
        verbose_name=_('Coach'),
        help_text=_('The coach of this team.')
    )
    
    # Team captain (optional)
    captain = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='captained_teams',
        verbose_name=_('Captain'),
        help_text=_('The captain of this team.')
    )
    
    # Team category
    CATEGORY_CHOICES = [
        ('senior', 'Senior'),
        ('junior', 'Junior'),
        ('youth', 'Youth'),
        ('mixed', 'Mixed'),
        ('women', "Women's"),
        ('men', "Men's"),
    ]
    
    category = models.CharField(
        _('Category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='senior',
        help_text=_('The category of the team.')
    )
    
    # Team level
    LEVEL_CHOICES = [
        ('recreational', 'Recreational'),
        ('competitive', 'Competitive'),
        ('professional', 'Professional'),
    ]
    
    level = models.CharField(
        _('Level'),
        max_length=20,
        choices=LEVEL_CHOICES,
        default='competitive',
        help_text=_('The competitive level of the team.')
    )
    
    # Team logo
    logo = models.ImageField(
        _('Team Logo'),
        upload_to='team_logos/',
        blank=True,
        null=True,
        help_text=_('The logo for this team.')
    )
    
    # Team colors
    primary_color = models.CharField(
        _('Primary Color'),
        max_length=20,
        blank=True,
        help_text=_('Primary color in hex format (e.g., #FF0000).')
    )
    
    secondary_color = models.CharField(
        _('Secondary Color'),
        max_length=20,
        blank=True,
        help_text=_('Secondary color in hex format (e.g., #00FF00).')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_coach_name(self):
        """Get the name of the coach."""
        if self.coach:
            return self.coach.get_full_name()
        return _('No coach assigned')
    
    def get_captain_name(self):
        """Get the name of the captain."""
        if self.captain:
            return self.captain.get_full_name()
        return _('No captain assigned')
    
    def get_player_count(self):
        """Get the number of players in this team."""
        return self.players.count()
    
    def get_active_player_count(self):
        """Get the number of active players in this team."""
        return self.players.filter(user__is_active=True).count()


class Player(models.Model):
    """
    Player model representing a player in a team.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='player_profiles',
        verbose_name=_('User'),
        help_text=_('The user associated with this player.')
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name=_('Team'),
        help_text=_('The team this player belongs to.')
    )
    
    # Player number (jersey number)
    player_number = models.PositiveIntegerField(
        _('Player Number'),
        null=True,
        blank=True,
        help_text=_('The player\'s jersey number.')
    )
    
    # Player position
    POSITION_CHOICES = [
        ('singles', 'Singles Player'),
        ('doubles', 'Doubles Player'),
        ('mixed', 'Mixed Doubles Player'),
        ('all_round', 'All-Round Player'),
        ('substitute', 'Substitute'),
    ]
    
    position = models.CharField(
        _('Position'),
        max_length=20,
        choices=POSITION_CHOICES,
        default='all_round',
        help_text=_('The player\'s primary position.')
    )
    
    # Skill level (1-10)
    skill_level = models.PositiveIntegerField(
        _('Skill Level'),
        default=5,
        help_text=_('Player skill level from 1 (beginner) to 10 (professional).'),
        choices=[(i, str(i)) for i in range(1, 11)]
    )
    
    # Player status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('injured', 'Injured'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text=_('Current status of the player.')
    )
    
    # Emergency contact information
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
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Player')
        verbose_name_plural = _('Players')
        ordering = ['team__name', 'user__last_name', 'user__first_name']
        unique_together = ['user', 'team']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['team']),
            models.Index(fields=['player_number']),
            models.Index(fields=['position']),
            models.Index(fields=['skill_level']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"
    
    def get_full_name(self):
        """Get the full name of the player."""
        return self.user.get_full_name()
    
    def is_available(self):
        """Check if player is available (not injured, suspended, or inactive)."""
        return self.status == 'active'
    
    def get_skill_display(self):
        """Get a display string for the skill level."""
        skill_map = {
            1: 'Beginner',
            2: 'Beginner',
            3: 'Beginner',
            4: 'Intermediate',
            5: 'Intermediate',
            6: 'Intermediate',
            7: 'Advanced',
            8: 'Advanced',
            9: 'Expert',
            10: 'Professional'
        }
        return skill_map.get(self.skill_level, f'Level {self.skill_level}')