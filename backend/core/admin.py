from django.contrib import admin
from .models import (
    Target, AssetType, Asset, ScanResult, 
    Dork, DorkResult, Relationship, Report, Alert
)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    """Admin configuration for the Target model."""
    
    list_display = ('name', 'target_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('target_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'tags')
    readonly_fields = ('slug', 'created_by', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    """Admin configuration for the AssetType model."""
    
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Admin configuration for the Asset model."""
    
    list_display = ('name', 'target', 'asset_type', 'value', 'is_verified', 'is_monitored', 'created_at')
    list_filter = ('asset_type', 'is_verified', 'is_monitored', 'created_at')
    search_fields = ('name', 'value', 'description', 'tags')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'last_checked')


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    """Admin configuration for the ScanResult model."""
    
    list_display = ('asset', 'scan_type', 'status', 'started_at', 'completed_at', 'created_at')
    list_filter = ('scan_type', 'status', 'created_at')
    search_fields = ('asset__name', 'scan_type', 'error_message')
    readonly_fields = ('created_by', 'created_at')


@admin.register(Dork)
class DorkAdmin(admin.ModelAdmin):
    """Admin configuration for the Dork model."""
    
    list_display = ('name', 'category', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'query', 'description', 'tags')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(DorkResult)
class DorkResultAdmin(admin.ModelAdmin):
    """Admin configuration for the DorkResult model."""
    
    list_display = ('dork', 'target', 'executed_by', 'executed_at')
    list_filter = ('executed_at',)
    search_fields = ('dork__name', 'target__name')
    readonly_fields = ('executed_by', 'executed_at')


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for the Relationship model."""
    
    list_display = ('source_asset', 'relationship_type', 'target_asset', 'confidence_score', 'created_at')
    list_filter = ('relationship_type', 'confidence_score', 'created_at')
    search_fields = ('source_asset__name', 'target_asset__name', 'description', 'evidence')
    readonly_fields = ('created_by', 'created_at', 'updated_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin configuration for the Report model."""
    
    list_display = ('name', 'target', 'report_type', 'format_type', 'created_by', 'created_at')
    list_filter = ('report_type', 'format_type', 'created_at')
    search_fields = ('name', 'target__name', 'content')
    readonly_fields = ('created_by', 'created_at')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for the Alert model."""
    
    list_display = ('title', 'target', 'asset', 'severity', 'status', 'created_at', 'acknowledged_by')
    list_filter = ('severity', 'status', 'created_at', 'acknowledged_at')
    search_fields = ('title', 'description', 'target__name', 'asset__name')
    readonly_fields = ('created_at', 'updated_at')