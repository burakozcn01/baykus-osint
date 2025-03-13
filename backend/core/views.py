from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Target, AssetType, Asset, ScanResult, 
    Dork, DorkResult, Relationship, Report, Alert
)
from .serializers import (
    TargetSerializer, AssetTypeSerializer, AssetSerializer,
    ScanResultSerializer, DorkSerializer, DorkResultSerializer,
    RelationshipSerializer, ReportSerializer, AlertSerializer
)


class TargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing targets.
    """
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_type', 'is_active', 'created_by']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get all assets for a specific target."""
        target = self.get_object()
        assets = Asset.objects.filter(target=target)
        serializer = AssetSerializer(assets, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all alerts for a specific target."""
        target = self.get_object()
        alerts = Alert.objects.filter(target=target)
        serializer = AlertSerializer(alerts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reports(self, request, pk=None):
        """Get all reports for a specific target."""
        target = self.get_object()
        reports = Report.objects.filter(target=target)
        serializer = ReportSerializer(reports, many=True, context={'request': request})
        return Response(serializer.data)


class AssetTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing asset types.
    """
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class AssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing assets.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target', 'asset_type', 'is_verified', 'is_monitored', 'created_by']
    search_fields = ['name', 'value', 'description', 'tags']
    ordering_fields = ['name', 'confidence_score', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        """Initiate a scan for a specific asset."""
        asset = self.get_object()
        
        # Get scan type from request data
        scan_type = request.data.get('scan_type')
        if not scan_type:
            return Response({'error': 'Scan type is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new scan result
        scan_result = ScanResult.objects.create(
            asset=asset,
            scan_type=scan_type,
            status='pending',
            created_by=request.user
        )
        
        # Update the asset's last_checked timestamp
        asset.last_checked = timezone.now()
        asset.save()
        
        # Here we would typically trigger a Celery task to perform the actual scan
        # For now, we'll just update the status to 'in_progress'
        scan_result.status = 'in_progress'
        scan_result.started_at = timezone.now()
        scan_result.save()
        
        serializer = ScanResultSerializer(scan_result, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def scan_results(self, request, pk=None):
        """Get all scan results for a specific asset."""
        asset = self.get_object()
        scan_results = ScanResult.objects.filter(asset=asset)
        serializer = ScanResultSerializer(scan_results, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get all relationships for a specific asset."""
        asset = self.get_object()
        source_relationships = Relationship.objects.filter(source_asset=asset)
        target_relationships = Relationship.objects.filter(target_asset=asset)
        
        source_serializer = RelationshipSerializer(source_relationships, many=True, context={'request': request})
        target_serializer = RelationshipSerializer(target_relationships, many=True, context={'request': request})
        
        return Response({
            'source_relationships': source_serializer.data,
            'target_relationships': target_serializer.data
        })


class ScanResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing scan results.
    """
    queryset = ScanResult.objects.all()
    serializer_class = ScanResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'scan_type', 'status', 'created_by']
    ordering_fields = ['created_at', 'started_at', 'completed_at']


class DorkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Google dork queries.
    """
    queryset = Dork.objects.all()
    serializer_class = DorkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'created_by']
    search_fields = ['name', 'query', 'description', 'category', 'tags']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a dork query for a specific target."""
        dork = self.get_object()
        
        # Get target from request data
        target_id = request.data.get('target_id')
        if not target_id:
            return Response({'error': 'Target ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target = Target.objects.get(pk=target_id)
        except Target.DoesNotExist:
            return Response({'error': 'Target not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create a new dork result
        dork_result = DorkResult.objects.create(
            dork=dork,
            target=target,
            executed_by=request.user,
            results=[]  # Empty results initially
        )
        
        # Here we would typically trigger a Celery task to perform the actual dork query
        # For now, we'll just return the created dork result
        
        serializer = DorkResultSerializer(dork_result, context={'request': request})
        return Response(serializer.data)


class DorkResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dork query results.
    """
    queryset = DorkResult.objects.all()
    serializer_class = DorkResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dork', 'target', 'executed_by']
    ordering_fields = ['executed_at']


class RelationshipViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing relationships between assets.
    """
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source_asset', 'target_asset', 'relationship_type', 'created_by']
    search_fields = ['description', 'evidence']
    ordering_fields = ['confidence_score', 'created_at', 'updated_at']


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing reports.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target', 'report_type', 'format_type', 'created_by']
    search_fields = ['name', 'content']
    ordering_fields = ['created_at']
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a report file."""
        report = self.get_object()
        
        if not report.file:
            return Response({'error': 'No file available for this report.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Here we would typically serve the file for download
        # For now, we'll just return the file URL
        
        return Response({'file_url': request.build_absolute_uri(report.file.url)})


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing alerts.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target', 'asset', 'severity', 'status', 'acknowledged_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'acknowledged_at']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        
        if alert.status == 'acknowledged':
            return Response({'error': 'Alert is already acknowledged.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response({'error': 'Alert is already resolved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alert.status = 'resolved'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_false_positive(self, request, pk=None):
        """Mark an alert as a false positive."""
        alert = self.get_object()
        
        if alert.status == 'false_positive':
            return Response({'error': 'Alert is already marked as false positive.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alert.status = 'false_positive'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)