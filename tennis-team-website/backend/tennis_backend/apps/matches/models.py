"""
Match models for Tennis Team Website.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from tennis_backend.apps.users.models import CustomUser
from tennis_backend.apps.teams.models import Team, Player
from tennis_backend.settings.base import MATCH_STATUSES, MATCH_TYPES, AVAILABILITY_STATUSES, RESPONSIBILITY_TYPES


class Match(models.Model):
    """
    Match model representing a tennis match.
    """
    match_date = models.DateField(
        _('Match Date'),
        help_text=_('The date of the match.')
    )
    
    start_time = models.TimeField(
        _('Start Time'),
        help_text=_('The start time of the match.')
    )
    
    end_time = models.TimeField(
        _('End Time'),
        null=True,
        blank=True,
        help_text=_('The expected end time of the match.')
    )
    
    location = models.CharField(
        _('Location'),
        max_length=255,
        help_text=_('The location where the match will be played.')
    )
    
    # Home and away teams
    home_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='home_matches',
        verbose_name=_('Home Team'),
        help_text=_('The home team for this match.')
    )
    
    away_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='away_matches',
        verbose_name=_('Away Team'),
        help_text=_('The away team for this match.')
    )
    
    # Match type
    match_type = models.CharField(
        _('Match Type'),
        max_length=20,
        choices=MATCH_TYPES,
        default='home',
        help_text=_('Whether this is a home, away, or neutral match.')
    )
    
    # Match status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=MATCH_STATUSES,
        default='scheduled',
        help_text=_('The current status of the match.')
    )
    
    # Opponent information (for matches against external teams)
    opponent_name = models.CharField(
        _('Opponent Name'),
        max_length=100,
        blank=True,
        help_text=_('The name of the opposing team (if not in our system).')
    )
    
    opponent_score = models.PositiveIntegerField(
        _('Opponent Score'),
        default=0,
        help_text=_('The score of the opposing team.')
    )
    
    our_score = models.PositiveIntegerField(
        _('Our Score'),
        default=0,
        help_text=_('Our team\'s score.')
    )
    
    # Court information
    court_number = models.CharField(
        _('Court Number'),
        max_length=20,
        blank=True,
        help_text=_('The court number where the match will be played.')
    )
    
    court_type = models.CharField(
        _('Court Type'),
        max_length=50,
        blank=True,
        choices=[
            ('clay', 'Clay'),
            ('grass', 'Grass'),
            ('hard', 'Hard Court'),
            ('indoor', 'Indoor'),
            ('carpet', 'Carpet'),
        ],
        help_text=_('The type of court surface.')
    )
    
    # Additional notes
    notes = models.TextField(
        _('Notes'),
        blank=True,
        help_text=_('Additional notes about the match.')
    )
    
    # Who created this match
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_matches',
        verbose_name=_('Created By'),
        help_text=_('The user who created this match.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Match')
        verbose_name_plural = _('Matches')
        ordering = ['match_date', 'start_time']
        indexes = [
            models.Index(fields=['match_date']),
            models.Index(fields=['start_time']),
            models.Index(fields=['home_team']),
            models.Index(fields=['away_team']),
            models.Index(fields=['status']),
            models.Index(fields=['match_type']),
        ]
    
    def __str__(self):
        if self.home_team and self.away_team:
            return f"{self.home_team.name} vs {self.away_team.name} on {self.match_date}"
        elif self.opponent_name:
            return f"vs {self.opponent_name} on {self.match_date}"
        else:
            return f"Match on {self.match_date} at {self.start_time}"
    
    def get_team_names(self):
        """Get the names of both teams."""
        home = self.home_team.name if self.home_team else _('TBD')
        away = self.away_team.name if self.away_team else self.opponent_name or _('TBD')
        return f"{home} vs {away}"
    
    def get_match_type_display(self):
        """Get display name for match type."""
        return dict(MATCH_TYPES).get(self.match_type, self.match_type)
    
    def get_status_display(self):
        """Get display name for status."""
        return dict(MATCH_STATUSES).get(self.status, self.status)
    
    def is_home_match(self):
        """Check if this is a home match."""
        return self.match_type == 'home'
    
    def is_away_match(self):
        """Check if this is an away match."""
        return self.match_type == 'away'
    
    def is_upcoming(self):
        """Check if the match is upcoming."""
        now = timezone.now()
        match_datetime = timezone.make_aware(
            timezone.datetime.combine(self.match_date, self.start_time)
        )
        return match_datetime > now and self.status not in ['cancelled', 'completed']
    
    def is_today(self):
        """Check if the match is today."""
        return self.match_date == timezone.now().date()
    
    def get_assigned_players(self):
        """Get all players assigned to this match."""
        return self.assignments.all()
    
    def get_available_players(self):
        """Get all players who are available for this match."""
        return self.availability.filter(status='available')
    
    def get_unavailable_players(self):
        """Get all players who are unavailable for this match."""
        return self.availability.filter(status='unavailable')
    
    def get_assigned_player_count(self):
        """Get the number of players assigned to this match."""
        return self.assignments.count()
    
    def get_available_player_count(self):
        """Get the number of players available for this match."""
        return self.availability.filter(status='available').count()


class PlayerAvailability(models.Model):
    """
    Model to track player availability for matches.
    """
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='availability',
        verbose_name=_('Player'),
        help_text=_('The player whose availability is being tracked.')
    )
    
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='availability',
        verbose_name=_('Match'),
        help_text=_('The match for which availability is being tracked.')
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=AVAILABILITY_STATUSES,
        default='unknown',
        help_text=_('The availability status of the player for this match.')
    )
    
    notes = models.TextField(
        _('Notes'),
        blank=True,
        help_text=_('Additional notes about the player\'s availability.')
    )
    
    responded_at = models.DateTimeField(
        _('Responded At'),
        null=True,
        blank=True,
        help_text=_('When the player responded with their availability.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Player Availability')
        verbose_name_plural = _('Player Availabilities')
        unique_together = ['player', 'match']
        ordering = ['match__match_date', 'match__start_time', 'player__user__last_name']
        indexes = [
            models.Index(fields=['player']),
            models.Index(fields=['match']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.player.get_full_name()} - {self.get_status_display()} for {self.match}"
    
    def get_status_display(self):
        """Get display name for status."""
        return dict(AVAILABILITY_STATUSES).get(self.status, self.status)
    
    def is_available(self):
        """Check if player is available."""
        return self.status == 'available'
    
    def is_unavailable(self):
        """Check if player is unavailable."""
        return self.status == 'unavailable'


class MatchAssignment(models.Model):
    """
    Model to track which players are assigned to which matches.
    """
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Match'),
        help_text=_('The match to which the player is assigned.')
    )
    
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Player'),
        help_text=_('The player assigned to this match.')
    )
    
    position = models.CharField(
        _('Position'),
        max_length=50,
        blank=True,
        help_text=_('The position the player will play (e.g., singles, doubles).')
    )
    
    is_captain = models.BooleanField(
        _('Is Captain'),
        default=False,
        help_text=_('Whether this player is the captain for this match.')
    )
    
    is_substitute = models.BooleanField(
        _('Is Substitute'),
        default=False,
        help_text=_('Whether this player is a substitute.')
    )
    
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_players',
        verbose_name=_('Assigned By'),
        help_text=_('The user who assigned this player to the match.')
    )
    
    assigned_at = models.DateTimeField(
        _('Assigned At'),
        auto_now_add=True,
        help_text=_('When the player was assigned to the match.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Match Assignment')
        verbose_name_plural = _('Match Assignments')
        unique_together = ['player', 'match']
        ordering = ['match__match_date', 'match__start_time', 'player__user__last_name']
        indexes = [
            models.Index(fields=['match']),
            models.Index(fields=['player']),
            models.Index(fields=['is_captain']),
            models.Index(fields=['is_substitute']),
        ]
    
    def __str__(self):
        return f"{self.player.get_full_name()} assigned to {self.match}"
    
    def get_position_display(self):
        """Get display name for position."""
        if self.position:
            return self.position
        return _('Not specified')


class Responsibility(models.Model):
    """
    Model to track responsibilities assigned to users for matches.
    """
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='responsibilities',
        verbose_name=_('Match'),
        help_text=_('The match for which this responsibility is assigned.')
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='responsibilities',
        verbose_name=_('User'),
        help_text=_('The user assigned to this responsibility.')
    )
    
    responsibility_type = models.CharField(
        _('Responsibility Type'),
        max_length=50,
        choices=RESPONSIBILITY_TYPES,
        help_text=_('The type of responsibility.')
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Additional details about this responsibility.')
    )
    
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_responsibilities',
        verbose_name=_('Assigned By'),
        help_text=_('The user who assigned this responsibility.')
    )
    
    assigned_at = models.DateTimeField(
        _('Assigned At'),
        auto_now_add=True,
        help_text=_('When this responsibility was assigned.')
    )
    
    completed = models.BooleanField(
        _('Completed'),
        default=False,
        help_text=_('Whether this responsibility has been completed.')
    )
    
    completed_at = models.DateTimeField(
        _('Completed At'),
        null=True,
        blank=True,
        help_text=_('When this responsibility was completed.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Responsibility')
        verbose_name_plural = _('Responsibilities')
        ordering = ['match__match_date', 'match__start_time', 'responsibility_type']
        indexes = [
            models.Index(fields=['match']),
            models.Index(fields=['user']),
            models.Index(fields=['responsibility_type']),
            models.Index(fields=['completed']),
        ]
    
    def __str__(self):
        return f"{self.get_responsibility_type_display()} - {self.user.get_full_name()} for {self.match}"
    
    def get_responsibility_type_display(self):
        """Get display name for responsibility type."""
        return dict(RESPONSIBILITY_TYPES).get(self.responsibility_type, self.responsibility_type)
    
    def mark_completed(self):
        """Mark this responsibility as completed."""
        self.completed = True
        self.completed_at = timezone.now()
        self.save()
    
    def mark_incomplete(self):
        """Mark this responsibility as incomplete."""
        self.completed = False
        self.completed_at = None
        self.save()