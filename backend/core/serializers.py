from rest_framework import serializers
from .models import (
    Target, AssetType, Asset, ScanResult, 
    Dork, DorkResult, Relationship, Report, Alert
)


class AssetTypeSerializer(serializers.ModelSerializer):
    """Serializer for the AssetType model."""
    
    class Meta:
        model = AssetType
        fields = ('id', 'name', 'description')


class TargetSerializer(serializers.ModelSerializer):
    """Serializer for the Target model."""
    
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Target
        fields = (
            'id', 'name', 'slug', 'target_type', 'description', 
            'tags', 'is_active', 'created_by', 'created_by_email', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_by', 'created_at', 'updated_at')
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the target."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new target and associate it with the current user."""
        user = self.context['request'].user
        target = Target.objects.create(created_by=user, **validated_data)
        return target


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for the Asset model."""
    
    asset_type_name = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = (
            'id', 'target', 'target_name', 'asset_type', 'asset_type_name', 
            'name', 'value', 'description', 'source', 'confidence_score', 
            'tags', 'is_verified', 'is_monitored', 'last_checked', 
            'created_by', 'created_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'last_checked')
    
    def get_asset_type_name(self, obj):
        """Get the name of the asset type."""
        return obj.asset_type.name
    
    def get_target_name(self, obj):
        """Get the name of the target."""
        return obj.target.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the asset."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new asset and associate it with the current user."""
        user = self.context['request'].user
        asset = Asset.objects.create(created_by=user, **validated_data)
        return asset


class ScanResultSerializer(serializers.ModelSerializer):
    """Serializer for the ScanResult model."""
    
    asset_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = ScanResult
        fields = (
            'id', 'asset', 'asset_name', 'scan_type', 'status', 
            'result_data', 'error_message', 'started_at', 'completed_at', 
            'created_by', 'created_by_email', 'created_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at')
    
    def get_asset_name(self, obj):
        """Get the name of the asset."""
        return obj.asset.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the scan result."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new scan result and associate it with the current user."""
        user = self.context['request'].user
        scan_result = ScanResult.objects.create(created_by=user, **validated_data)
        return scan_result


class DorkSerializer(serializers.ModelSerializer):
    """Serializer for the Dork model."""
    
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Dork
        fields = (
            'id', 'name', 'query', 'description', 'category', 
            'tags', 'created_by', 'created_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the dork."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new dork and associate it with the current user."""
        user = self.context['request'].user
        dork = Dork.objects.create(created_by=user, **validated_data)
        return dork


class DorkResultSerializer(serializers.ModelSerializer):
    """Serializer for the DorkResult model."""
    
    dork_name = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    executed_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = DorkResult
        fields = (
            'id', 'dork', 'dork_name', 'target', 'target_name', 
            'results', 'executed_at', 'executed_by', 'executed_by_email'
        )
        read_only_fields = ('id', 'executed_at', 'executed_by')
    
    def get_dork_name(self, obj):
        """Get the name of the dork."""
        return obj.dork.name
    
    def get_target_name(self, obj):
        """Get the name of the target."""
        return obj.target.name
    
    def get_executed_by_email(self, obj):
        """Get the email of the user who executed the dork."""
        return obj.executed_by.email if obj.executed_by else None
    
    def create(self, validated_data):
        """Create a new dork result and associate it with the current user."""
        user = self.context['request'].user
        dork_result = DorkResult.objects.create(executed_by=user, **validated_data)
        return dork_result


class RelationshipSerializer(serializers.ModelSerializer):
    """Serializer for the Relationship model."""
    
    source_asset_name = serializers.SerializerMethodField()
    target_asset_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Relationship
        fields = (
            'id', 'source_asset', 'source_asset_name', 'target_asset', 
            'target_asset_name', 'relationship_type', 'description', 
            'confidence_score', 'evidence', 'created_by', 'created_by_email', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_source_asset_name(self, obj):
        """Get the name of the source asset."""
        return obj.source_asset.name
    
    def get_target_asset_name(self, obj):
        """Get the name of the target asset."""
        return obj.target_asset.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the relationship."""
        return obj.created_by.email if obj.created_by else None
    
    def create(self, validated_data):
        """Create a new relationship and associate it with the current user."""
        user = self.context['request'].user
        relationship = Relationship.objects.create(created_by=user, **validated_data)
        return relationship


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for the Report model."""
    
    target_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = (
            'id', 'target', 'target_name', 'name', 'report_type', 
            'format_type', 'configuration', 'content', 'file', 'file_url',
            'created_by', 'created_by_email', 'created_at'
        )
        read_only_fields = ('id', 'file', 'created_by', 'created_at')
    
    def get_target_name(self, obj):
        """Get the name of the target."""
        return obj.target.name
    
    def get_created_by_email(self, obj):
        """Get the email of the user who created the report."""
        return obj.created_by.email if obj.created_by else None
    
    def get_file_url(self, obj):
        """Get the URL of the report file."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        """Create a new report and associate it with the current user."""
        user = self.context['request'].user
        report = Report.objects.create(created_by=user, **validated_data)
        return report


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for the Alert model."""
    
    target_name = serializers.SerializerMethodField()
    asset_name = serializers.SerializerMethodField()
    acknowledged_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = (
            'id', 'target', 'target_name', 'asset', 'asset_name', 
            'title', 'description', 'severity', 'status', 
            'previous_value', 'current_value', 'created_at', 'updated_at', 
            'acknowledged_by', 'acknowledged_by_email', 'acknowledged_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_target_name(self, obj):
        """Get the name of the target."""
        return obj.target.name
    
    def get_asset_name(self, obj):
        """Get the name of the asset."""
        return obj.asset.name if obj.asset else None
    
    def get_acknowledged_by_email(self, obj):
        """Get the email of the user who acknowledged the alert."""
        return obj.acknowledged_by.email if obj.acknowledged_by else None