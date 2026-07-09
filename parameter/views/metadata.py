"""
元数据视图模块
提供元数据的增删改查功能
"""
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import login_required, role_required
from ..models import Metadata
from ..utils.pagination import paginate_queryset

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class MetadataListView(View):
    """
    元数据列表视图
    展示系统预设的常用元数据配置
    """
    def get(self, request):
        logger.info(f"[MetadataListView] 开始查询元数据列表，请求路径: {request.path}")
        try:
            metadata_list = Metadata.objects.all()
            logger.info(f"[MetadataListView] 元数据查询完成，记录数: {metadata_list.count()}")
            
            search_name = request.GET.get('search', '')
            if search_name:
                metadata_list = metadata_list.filter(name__icontains=search_name) | metadata_list.filter(field_name_en__icontains=search_name) | metadata_list.filter(description__icontains=search_name)
                logger.info(f"[MetadataListView] 搜索后记录数: {metadata_list.count()}")
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            logger.info(f"[MetadataListView] 当前用户可编辑: {is_editable}")
            
            pagination, metadata_list = paginate_queryset(request, metadata_list)
            
            context = {
                'metadata_list': metadata_list,
                'is_editable': is_editable,
                'search_name': search_name,
                'pagination': pagination,
            }
            logger.info(f"[MetadataListView] 元数据列表查询成功，即将渲染模板")
            return render(request, 'parameter/metadata_list.html', context)
        except Exception as e:
            logger.error(f"[MetadataListView] 元数据列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataCreateView(View):
    """
    元数据创建视图
    仅管理员和技术人员可访问，用于创建新的元数据配置
    """
    def get(self, request):
        logger.info(f"[MetadataCreateView] 加载创建元数据页面")
        context = {
            'field_types': Metadata.FIELD_TYPE_CHOICES,
            'control_types': Metadata.CONTROL_TYPE_CHOICES,
        }
        return render(request, 'parameter/metadata_create.html', context)
    
    def post(self, request):
        logger.info(f"[MetadataCreateView] 创建元数据")
        try:
            metadata = Metadata(
                name=request.POST.get('name'),
                field_name_en=request.POST.get('field_name_en'),
                field_type=request.POST.get('field_type'),
                length=request.POST.get('length') or None,
                decimal_places=request.POST.get('decimal_places') or None,
                control_type=request.POST.get('control_type'),
                default_value=request.POST.get('default_value'),
                is_required=request.POST.get('is_required') == 'on',
                validation_rule=request.POST.get('validation_rule'),
                description=request.POST.get('description'),
            )
            metadata.save()
            logger.info(f"[MetadataCreateView] 元数据创建成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Exception as e:
            logger.error(f"[MetadataCreateView] 创建元数据失败: {str(e)}", exc_info=True)
            context = {
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/metadata_create.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataEditView(View):
    """
    元数据编辑视图
    仅管理员和技术人员可访问，用于修改元数据配置
    """
    def get(self, request, metadata_id):
        logger.info(f"[MetadataEditView] 加载编辑元数据页面，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            context = {
                'metadata': metadata,
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
            }
            return render(request, 'parameter/metadata_edit.html', context)
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataEditView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})
    
    def post(self, request, metadata_id):
        logger.info(f"[MetadataEditView] 更新元数据，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            metadata.name = request.POST.get('name')
            metadata.field_name_en = request.POST.get('field_name_en')
            metadata.field_type = request.POST.get('field_type')
            metadata.length = request.POST.get('length') or None
            metadata.decimal_places = request.POST.get('decimal_places') or None
            metadata.control_type = request.POST.get('control_type')
            metadata.default_value = request.POST.get('default_value')
            metadata.is_required = request.POST.get('is_required') == 'on'
            metadata.validation_rule = request.POST.get('validation_rule')
            metadata.description = request.POST.get('description')
            metadata.save()
            logger.info(f"[MetadataEditView] 元数据更新成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataEditView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})
        except Exception as e:
            logger.error(f"[MetadataEditView] 更新元数据失败: {str(e)}", exc_info=True)
            metadata = Metadata.objects.get(id=metadata_id)
            context = {
                'metadata': metadata,
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
                'error': str(e),
            }
            return render(request, 'parameter/metadata_edit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataDeleteView(View):
    """
    元数据删除视图
    仅管理员和技术人员可访问，用于删除元数据配置
    """
    def get(self, request, metadata_id):
        logger.info(f"[MetadataDeleteView] 删除元数据，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            metadata.delete()
            logger.info(f"[MetadataDeleteView] 元数据删除成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataDeleteView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})
