"""
参数表视图模块
提供参数表的增删改查功能
"""
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import login_required, role_required
from ..models import ParameterTable, FieldDefinition, Metadata

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ParameterTableListView(View):
    """
    参数表列表视图
    展示所有参数表的业务说明底账，支持按业务领域、状态和名称搜索过滤
    """
    def get(self, request):
        logger.info(f"[ParameterTableListView] 开始查询参数表清单，请求路径: {request.path}")
        try:
            tables = ParameterTable.objects.all()
            logger.info(f"[ParameterTableListView] 初始查询参数表记录数: {tables.count()}")
            
            domain_filter = request.GET.get('domain', '')
            status_filter = request.GET.get('status', '')
            search_name = request.GET.get('search', '')
            
            logger.info(f"[ParameterTableListView] 查询条件 - domain: '{domain_filter}', status: '{status_filter}', search: '{search_name}'")
            
            if domain_filter:
                tables = tables.filter(domain=domain_filter)
                logger.info(f"[ParameterTableListView] 按domain过滤后记录数: {tables.count()}")
            
            if status_filter:
                tables = tables.filter(status=status_filter)
                logger.info(f"[ParameterTableListView] 按status过滤后记录数: {tables.count()}")
            
            if search_name:
                tables = tables.filter(name_en__icontains=search_name) | tables.filter(name__icontains=search_name) | tables.filter(business_description__icontains=search_name)
                logger.info(f"[ParameterTableListView] 按搜索词过滤后记录数: {tables.count()}")
            
            domains = ParameterTable.objects.values_list('domain', flat=True).distinct()
            logger.info(f"[ParameterTableListView] 获取到 {len(list(domains))} 个不同的业务领域")
            
            statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            
            context = {
                'tables': tables,
                'domains': domains,
                'statuses': statuses,
                'domain_filter': domain_filter,
                'status_filter': status_filter,
                'search_name': search_name,
                'is_editable': is_editable,
            }
            logger.info(f"[ParameterTableListView] 参数表清单查询成功，即将渲染模板")
            return render(request, 'parameter/table_list.html', context)
        except Exception as e:
            logger.error(f"[ParameterTableListView] 参数表清单查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(login_required, name='dispatch')
class ParameterTableDetailView(View):
    """
    参数表详情视图
    展示参数表的详细信息，包括字段定义列表
    """
    def get(self, request, table_id):
        logger.info(f"[ParameterTableDetailView] 开始查询参数表详情，table_id: {table_id}")
        try:
            table = ParameterTable.objects.filter(id=table_id).first()
            logger.info(f"[ParameterTableDetailView] 参数表查询结果: {'存在' if table else '不存在'}, table_id: {table_id}")
            
            fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            logger.info(f"[ParameterTableDetailView] 字段定义查询完成，记录数: {fields.count()}")
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            
            context = {
                'table': table,
                'fields': fields,
                'is_editable': is_editable,
            }
            logger.info(f"[ParameterTableDetailView] 参数表详情查询成功，即将渲染模板")
            return render(request, 'parameter/table_detail.html', context)
        except Exception as e:
            logger.error(f"[ParameterTableDetailView] 参数表详情查询失败，table_id: {table_id}, 错误: {str(e)}", exc_info=True)
            raise


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ParameterTableCreateView(View):
    """
    参数表创建视图
    仅管理员和技术人员可访问，用于创建新的参数表
    """
    def get(self, request):
        logger.info(f"[ParameterTableCreateView] 加载创建参数表页面")
        statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
        context = {'statuses': statuses}
        return render(request, 'parameter/table_create.html', context)
    
    def post(self, request):
        logger.info(f"[ParameterTableCreateView] 创建参数表")
        try:
            table = ParameterTable(
                name_en=request.POST.get('name_en'),
                name=request.POST.get('name'),
                business_description=request.POST.get('business_description'),
                domain=request.POST.get('domain'),
                owner=request.POST.get('owner'),
                status=request.POST.get('status', 'draft'),
                is_simple=request.POST.get('is_simple') == 'on',
            )
            table.save()
            logger.info(f"[ParameterTableCreateView] 参数表创建成功，name_en: {table.name_en}, name: {table.name}, is_simple: {table.is_simple}")
            return redirect('table_list')
        except Exception as e:
            logger.error(f"[ParameterTableCreateView] 创建参数表失败: {str(e)}", exc_info=True)
            statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
            context = {
                'statuses': statuses,
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/table_create.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ParameterTableEditView(View):
    """
    参数表编辑视图
    仅管理员和技术人员可访问，用于修改参数表信息
    
    SIMPLE表（is_simple=True）不可编辑，仅展示
    """
    def get(self, request, table_id):
        logger.info(f"[ParameterTableEditView] 加载编辑参数表页面，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[ParameterTableEditView] SIMPLE表不可编辑，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可编辑'})
            statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
            context = {'table': table, 'statuses': statuses}
            return render(request, 'parameter/table_edit.html', context)
        except ParameterTable.DoesNotExist:
            logger.error(f"[ParameterTableEditView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})
    
    def post(self, request, table_id):
        logger.info(f"[ParameterTableEditView] 更新参数表，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[ParameterTableEditView] SIMPLE表不可更新，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可更新'})
            table.name_en = request.POST.get('name_en')
            table.name = request.POST.get('name')
            table.business_description = request.POST.get('business_description')
            table.domain = request.POST.get('domain')
            table.owner = request.POST.get('owner')
            table.status = request.POST.get('status', 'draft')
            table.save()
            logger.info(f"[ParameterTableEditView] 参数表更新成功，name_en: {table.name_en}, name: {table.name}")
            return redirect('table_list')
        except ParameterTable.DoesNotExist:
            logger.error(f"[ParameterTableEditView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})
        except Exception as e:
            logger.error(f"[ParameterTableEditView] 更新参数表失败: {str(e)}", exc_info=True)
            table = ParameterTable.objects.get(id=table_id)
            statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
            context = {
                'table': table,
                'statuses': statuses,
                'error': str(e),
            }
            return render(request, 'parameter/table_edit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ParameterTableDeleteView(View):
    """
    参数表删除视图
    仅管理员和技术人员可访问，用于删除参数表
    
    SIMPLE表（is_simple=True）不可删除，仅展示
    """
    def get(self, request, table_id):
        logger.info(f"[ParameterTableDeleteView] 删除参数表，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[ParameterTableDeleteView] SIMPLE表不可删除，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可删除'})
            table.delete()
            logger.info(f"[ParameterTableDeleteView] 参数表删除成功，name: {table.name}")
            return redirect('table_list')
        except ParameterTable.DoesNotExist:
            logger.error(f"[ParameterTableDeleteView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ParameterTableFieldConfigurationView(View):
    """
    参数表字段配置视图
    展示参数表的字段列表，支持添加、编辑、删除字段
    字段可以选择元数据所列的字段，也可以自定义
    """
    def get(self, request, table_id):
        logger.info(f"[ParameterTableFieldConfigurationView] 加载参数表字段配置页面，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[ParameterTableFieldConfigurationView] SIMPLE表不可配置字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可配置字段'})
            
            fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            metadata_list = Metadata.objects.all()
            
            context = {
                'table': table,
                'fields': fields,
                'metadata_list': metadata_list,
            }
            logger.info(f"[ParameterTableFieldConfigurationView] 参数表字段配置页面加载成功，字段数: {fields.count()}")
            return render(request, 'parameter/table_fields.html', context)
        except ParameterTable.DoesNotExist:
            logger.error(f"[ParameterTableFieldConfigurationView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class FieldAddView(View):
    """
    字段添加视图
    支持从元数据选择字段或自定义字段
    """
    def get(self, request, table_id):
        logger.info(f"[FieldAddView] 加载添加字段页面，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[FieldAddView] SIMPLE表不可添加字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可添加字段'})
            
            metadata_list = Metadata.objects.all()
            
            context = {
                'table': table,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
            }
            return render(request, 'parameter/field_add.html', context)
        except ParameterTable.DoesNotExist:
            logger.error(f"[FieldAddView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})
    
    def post(self, request, table_id):
        logger.info(f"[FieldAddView] 添加字段，table_id: {table_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[FieldAddView] SIMPLE表不可添加字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可添加字段'})
            
            metadata_id = request.POST.get('metadata')
            is_custom = request.POST.get('is_custom') == 'on'
            
            if metadata_id and not is_custom:
                metadata = Metadata.objects.get(id=metadata_id)
                field = FieldDefinition(
                    parameter_table=table,
                    metadata=metadata,
                    field_name=metadata.field_name_en or metadata.name,
                    display_name=metadata.name,
                    field_type=metadata.field_type,
                    length=metadata.length,
                    decimal_places=metadata.decimal_places,
                    control_type=metadata.control_type,
                    storage_type=request.POST.get('storage_type', 'code_only'),
                    is_visible=True,
                    is_required=metadata.is_required,
                    validation_rule=metadata.validation_rule,
                    sort_order=request.POST.get('sort_order', 0),
                )
            else:
                field = FieldDefinition(
                    parameter_table=table,
                    field_name=request.POST.get('field_name'),
                    display_name=request.POST.get('display_name'),
                    field_type=request.POST.get('field_type'),
                    length=request.POST.get('length') or None,
                    decimal_places=request.POST.get('decimal_places') or None,
                    control_type=request.POST.get('control_type'),
                    storage_type=request.POST.get('storage_type', 'code_only'),
                    is_visible=True,
                    is_required=request.POST.get('is_required') == 'on',
                    validation_rule=request.POST.get('validation_rule'),
                    sort_order=request.POST.get('sort_order', 0),
                    is_custom=True,
                )
            
            field.save()
            logger.info(f"[FieldAddView] 字段添加成功，field_name: {field.field_name}")
            return redirect('table_fields', table_id=table_id)
        except Exception as e:
            logger.error(f"[FieldAddView] 添加字段失败: {str(e)}", exc_info=True)
            table = ParameterTable.objects.get(id=table_id)
            metadata_list = Metadata.objects.all()
            context = {
                'table': table,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/field_add.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class FieldEditView(View):
    """
    字段编辑视图
    编辑参数表的字段配置
    """
    def get(self, request, table_id, field_id):
        logger.info(f"[FieldEditView] 加载编辑字段页面，table_id: {table_id}, field_id: {field_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[FieldEditView] SIMPLE表不可编辑字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可编辑字段'})
            
            field = FieldDefinition.objects.get(id=field_id)
            metadata_list = Metadata.objects.all()
            
            context = {
                'table': table,
                'field': field,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
            }
            return render(request, 'parameter/field_edit.html', context)
        except ParameterTable.DoesNotExist:
            logger.error(f"[FieldEditView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})
        except FieldDefinition.DoesNotExist:
            logger.error(f"[FieldEditView] 字段不存在，field_id: {field_id}")
            return render(request, 'parameter/error.html', {'message': '字段不存在'})
    
    def post(self, request, table_id, field_id):
        logger.info(f"[FieldEditView] 更新字段，table_id: {table_id}, field_id: {field_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[FieldEditView] SIMPLE表不可更新字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可更新字段'})
            
            field = FieldDefinition.objects.get(id=field_id)
            
            metadata_id = request.POST.get('metadata')
            if metadata_id:
                field.metadata = Metadata.objects.get(id=metadata_id)
            else:
                field.metadata = None
            
            field.field_name = request.POST.get('field_name')
            field.display_name = request.POST.get('display_name')
            field.field_type = request.POST.get('field_type')
            field.length = request.POST.get('length') or None
            field.decimal_places = request.POST.get('decimal_places') or None
            field.control_type = request.POST.get('control_type')
            field.storage_type = request.POST.get('storage_type')
            field.is_visible = request.POST.get('is_visible') == 'on'
            field.is_required = request.POST.get('is_required') == 'on'
            field.validation_rule = request.POST.get('validation_rule')
            field.sort_order = request.POST.get('sort_order', 0)
            field.is_custom = request.POST.get('is_custom') == 'on'
            
            field.save()
            logger.info(f"[FieldEditView] 字段更新成功，field_name: {field.field_name}")
            return redirect('table_fields', table_id=table_id)
        except Exception as e:
            logger.error(f"[FieldEditView] 更新字段失败: {str(e)}", exc_info=True)
            table = ParameterTable.objects.get(id=table_id)
            field = FieldDefinition.objects.get(id=field_id)
            metadata_list = Metadata.objects.all()
            context = {
                'table': table,
                'field': field,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
                'error': str(e),
            }
            return render(request, 'parameter/field_edit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class FieldDeleteView(View):
    """
    字段删除视图
    删除参数表的字段配置
    """
    def get(self, request, table_id, field_id):
        logger.info(f"[FieldDeleteView] 删除字段，table_id: {table_id}, field_id: {field_id}")
        try:
            table = ParameterTable.objects.get(id=table_id)
            if table.is_simple:
                logger.warning(f"[FieldDeleteView] SIMPLE表不可删除字段，table_id: {table_id}")
                return render(request, 'parameter/error.html', {'message': 'SIMPLE表仅展示，不可删除字段'})
            
            field = FieldDefinition.objects.get(id=field_id)
            field.delete()
            logger.info(f"[FieldDeleteView] 字段删除成功，field_name: {field.field_name}")
            return redirect('table_fields', table_id=table_id)
        except ParameterTable.DoesNotExist:
            logger.error(f"[FieldDeleteView] 参数表不存在，table_id: {table_id}")
            return render(request, 'parameter/error.html', {'message': '参数表不存在'})
        except FieldDefinition.DoesNotExist:
            logger.error(f"[FieldDeleteView] 字段不存在，field_id: {field_id}")
            return render(request, 'parameter/error.html', {'message': '字段不存在'})
