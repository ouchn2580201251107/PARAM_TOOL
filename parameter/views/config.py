"""
配置视图模块
提供配置脚本和INDEXID配置的管理功能
"""
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import login_required, admin_required, role_required
from ..models import ConfigScript, ProductTableConfig
from ..utils.pagination import paginate_queryset

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ConfigScriptListView(View):
    """
    配置脚本列表视图
    展示所有配置脚本，支持按状态和需求编号筛选
    """
    def get(self, request):
        logger.info(f"[ConfigScriptListView] 开始查询配置脚本列表，请求路径: {request.path}")
        try:
            scripts = ConfigScript.objects.all().order_by('-submitted_at')
            logger.info(f"[ConfigScriptListView] 配置脚本查询完成，记录数: {scripts.count()}")
            
            status_filter = request.GET.get('status', '')
            req_no_filter = request.GET.get('req_no', '')
            logger.info(f"[ConfigScriptListView] 查询条件 - status: '{status_filter}', req_no: '{req_no_filter}'")
            
            if status_filter:
                scripts = scripts.filter(status=status_filter)
                logger.info(f"[ConfigScriptListView] 按状态过滤后记录数: {scripts.count()}")
            
            if req_no_filter:
                scripts = scripts.filter(requirement__requirement_no__icontains=req_no_filter)
                logger.info(f"[ConfigScriptListView] 按需求编号过滤后记录数: {scripts.count()}")
            
            pagination, scripts = paginate_queryset(request, scripts)
            
            context = {
                'scripts': scripts,
                'status_filter': status_filter,
                'req_no_filter': req_no_filter,
                'statuses': ConfigScript.STATUS_CHOICES,
                'pagination': pagination,
            }
            logger.info(f"[ConfigScriptListView] 配置脚本列表查询成功，即将渲染模板")
            return render(request, 'parameter/config_script_list.html', context)
        except Exception as e:
            logger.error(f"[ConfigScriptListView] 配置脚本列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(admin_required, name='dispatch')
class ConfigScriptSubmitView(View):
    """
    配置脚本提交视图
    仅管理员可访问，用于提交配置脚本
    """
    def post(self, request, script_id):
        logger.info(f"[ConfigScriptSubmitView] 提交配置脚本，script_id: {script_id}")
        try:
            script = ConfigScript.objects.get(id=script_id)
            script.status = 'submitted'
            script.save()
            logger.info(f"[ConfigScriptSubmitView] 配置脚本提交成功，script_id: {script_id}")
            return redirect('config_scripts')
        except ConfigScript.DoesNotExist:
            logger.error(f"[ConfigScriptSubmitView] 配置脚本不存在，script_id: {script_id}")
            return render(request, 'parameter/error.html', {'message': '配置脚本不存在'})
        except Exception as e:
            logger.error(f"[ConfigScriptSubmitView] 提交配置脚本失败: {str(e)}", exc_info=True)
            raise


@method_decorator(login_required, name='dispatch')
class ProductTableConfigListView(View):
    """
    成品表复用配置列表视图
    展示所有成品表复用配置
    """
    def get(self, request):
        logger.info(f"[ProductTableConfigListView] 开始查询成品表复用配置列表，请求路径: {request.path}")
        try:
            configs = ProductTableConfig.objects.all()
            logger.info(f"[ProductTableConfigListView] 成品表复用配置查询完成，记录数: {configs.count()}")
            
            search_name = request.GET.get('search', '')
            if search_name:
                configs = configs.filter(index_id__icontains=search_name) | configs.filter(business_name__icontains=search_name) | configs.filter(business_description__icontains=search_name)
                logger.info(f"[ProductTableConfigListView] 搜索后记录数: {configs.count()}")
            
            product_table = request.GET.get('product_table', '')
            if product_table:
                configs = configs.filter(product_table=product_table)
                logger.info(f"[ProductTableConfigListView] 按成品表过滤后记录数: {configs.count()}")
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            
            pagination, configs = paginate_queryset(request, configs)
            
            context = {
                'configs': configs,
                'is_editable': is_editable,
                'search_name': search_name,
                'product_table': product_table,
                'product_tables': ProductTableConfig.PRODUCT_TABLE_CHOICES,
                'pagination': pagination,
            }
            logger.info(f"[ProductTableConfigListView] 成品表复用配置列表查询成功，即将渲染模板")
            return render(request, 'parameter/product_table_configs.html', context)
        except Exception as e:
            logger.error(f"[ProductTableConfigListView] 成品表复用配置列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ProductTableConfigCreateView(View):
    """
    成品表复用配置创建视图
    仅管理员和技术人员可访问，用于创建新的成品表复用配置
    
    创建配置时会自动生成物理表名，规则：根据大小写区分词并增加下划线，转换为大写
    示例：archTech -> ARCH_TECH
    """
    def get(self, request):
        logger.info(f"[ProductTableConfigCreateView] 加载创建成品表复用配置页面")
        context = {
            'product_tables': ProductTableConfig.PRODUCT_TABLE_CHOICES,
        }
        return render(request, 'parameter/product_table_config_create.html', context)
    
    def post(self, request):
        logger.info(f"[ProductTableConfigCreateView] 创建成品表复用配置")
        try:
            config = ProductTableConfig(
                product_table=request.POST.get('product_table', 'SIMPLE'),
                index_id=request.POST.get('index_id'),
                business_name=request.POST.get('business_name'),
                business_description=request.POST.get('business_description'),
            )
            config.save()
            logger.info(f"[ProductTableConfigCreateView] 成品表复用配置创建成功，product_table: {config.product_table}, index_id: {config.index_id}, table_name: {config.table_name}")
            return redirect('product_table_config_list')
        except Exception as e:
            logger.error(f"[ProductTableConfigCreateView] 创建成品表复用配置失败: {str(e)}", exc_info=True)
            context = {
                'error': str(e),
                'data': request.POST,
                'product_tables': ProductTableConfig.PRODUCT_TABLE_CHOICES,
            }
            return render(request, 'parameter/product_table_config_create.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ProductTableConfigEditView(View):
    """
    成品表复用配置编辑视图
    仅管理员和技术人员可访问，用于修改成品表复用配置
    """
    def get(self, request, config_id):
        logger.info(f"[ProductTableConfigEditView] 加载编辑成品表复用配置页面，config_id: {config_id}")
        try:
            config = ProductTableConfig.objects.get(id=config_id)
            context = {
                'config': config,
                'product_tables': ProductTableConfig.PRODUCT_TABLE_CHOICES,
            }
            return render(request, 'parameter/product_table_config_edit.html', context)
        except ProductTableConfig.DoesNotExist:
            logger.error(f"[ProductTableConfigEditView] 成品表复用配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': '成品表复用配置不存在'})
    
    def post(self, request, config_id):
        logger.info(f"[ProductTableConfigEditView] 更新成品表复用配置，config_id: {config_id}")
        try:
            config = ProductTableConfig.objects.get(id=config_id)
            config.product_table = request.POST.get('product_table', 'SIMPLE')
            config.index_id = request.POST.get('index_id')
            config.business_name = request.POST.get('business_name')
            config.business_description = request.POST.get('business_description')
            config.save()
            logger.info(f"[ProductTableConfigEditView] 成品表复用配置更新成功，product_table: {config.product_table}, index_id: {config.index_id}, table_name: {config.table_name}")
            return redirect('product_table_config_list')
        except ProductTableConfig.DoesNotExist:
            logger.error(f"[ProductTableConfigEditView] 成品表复用配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': '成品表复用配置不存在'})
        except Exception as e:
            logger.error(f"[ProductTableConfigEditView] 更新成品表复用配置失败: {str(e)}", exc_info=True)
            config = ProductTableConfig.objects.get(id=config_id)
            context = {
                'config': config,
                'error': str(e),
                'product_tables': ProductTableConfig.PRODUCT_TABLE_CHOICES,
            }
            return render(request, 'parameter/product_table_config_edit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class ProductTableConfigDeleteView(View):
    """
    成品表复用配置删除视图
    仅管理员和技术人员可访问，用于删除成品表复用配置
    """
    def get(self, request, config_id):
        logger.info(f"[ProductTableConfigDeleteView] 删除成品表复用配置，config_id: {config_id}")
        try:
            config = ProductTableConfig.objects.get(id=config_id)
            config.delete()
            logger.info(f"[ProductTableConfigDeleteView] 成品表复用配置删除成功，index_id: {config.index_id}")
            return redirect('product_table_config_list')
        except ProductTableConfig.DoesNotExist:
            logger.error(f"[ProductTableConfigDeleteView] 成品表复用配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': '成品表复用配置不存在'})
