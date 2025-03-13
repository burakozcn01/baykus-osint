from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
import uuid

User = get_user_model()


class Target(models.Model):
    """
    Target model represents entities that are the focus of OSINT investigations.
    This could be a person, organization, domain, etc.
    """
    TARGET_TYPES = (
        ('person', 'Person'),
        ('organization', 'Organization'),
        ('domain', 'Domain'),
        ('ip', 'IP Address'),
        ('other', 'Other')
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    description = models.TextField(blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_targets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_target_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a slug based on the name
            self.slug = slugify(self.name)
            
            # Ensure slug uniqueness
            orig_slug = self.slug
            counter = 1
            while Target.objects.filter(slug=self.slug).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)


class AssetType(models.Model):
    """
    AssetType model represents different types of digital assets that can be discovered.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    Asset model represents digital footprints or resources associated with a target.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    name = models.CharField(max_length=255)
    value = models.TextField()
    description = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    is_verified = models.BooleanField(default=False)
    
    # For monitoring
    is_monitored = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['target', 'asset_type', 'value']
    
    def __str__(self):
        return f"{self.name} ({self.asset_type})"


class ScanResult(models.Model):
    """
    ScanResult model stores the results of scans performed on assets.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='scan_results')
    scan_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Metadata
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_scans')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.scan_type} scan for {self.asset}"


class Dork(models.Model):
    """
    Dork model represents saved Google dork queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    query = models.TextField()
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_dorks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DorkResult(models.Model):
    """
    DorkResult model stores the results of executed dork queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dork = models.ForeignKey(Dork, on_delete=models.CASCADE, related_name='results')
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='dork_results')
    results = models.JSONField(default=list)
    
    # Metadata
    executed_at = models.DateTimeField(auto_now_add=True)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='executed_dorks')
    
    class Meta:
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"Results for {self.dork.name} on {self.target.name}"


class Relationship(models.Model):
    """
    Relationship model represents connections between assets.
    """
    RELATIONSHIP_TYPES = (
        ('owner', 'Owner'),
        ('user', 'User'),
        ('admin', 'Administrator'),
        ('associated', 'Associated'),
        ('similar', 'Similar'),
        ('linked', 'Linked'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='source_relationships')
    target_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='target_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    evidence = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-confidence_score']
        unique_together = ['source_asset', 'target_asset', 'relationship_type']
    
    def __str__(self):
        return f"{self.source_asset} {self.get_relationship_type_display()} {self.target_asset}"


class Report(models.Model):
    """
    Report model represents generated reports for targets.
    """
    REPORT_TYPES = (
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('asset_inventory', 'Asset Inventory'),
        ('vulnerability', 'Vulnerability Report'),
        ('timeline', 'Timeline Analysis'),
        ('custom', 'Custom Report'),
    )
    
    FORMAT_TYPES = (
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('csv', 'CSV'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    format_type = models.CharField(max_length=10, choices=FORMAT_TYPES)
    configuration = models.JSONField(default=dict)  # Store report configuration
    content = models.TextField(blank=True)  # For HTML reports
    file = models.FileField(upload_to='reports/', null=True, blank=True)  # For PDF, CSV, etc.
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} for {self.target.name}"


class Alert(models.Model):
    """
    Alert model represents notifications about asset changes or findings.
    """
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='alerts')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    
    # Change detection
    previous_value = models.TextField(blank=True)
    current_value = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) for {self.target.name}"