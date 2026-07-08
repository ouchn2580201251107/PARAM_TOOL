"""
配置视图模块
提供配置脚本和INDEXID配置的管理功能
"""
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import login_required, admin_required, role_required
from ..models import ConfigScript, IndexIdConfig

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
            
            context = {
                'scripts': scripts,
                'status_filter': status_filter,
                'req_no_filter': req_no_filter,
                'statuses': ConfigScript.STATUS_CHOICES,
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
class IndexIdConfigListView(View):
    """
    INDEXID配置列表视图
    展示所有INDEXID配置
    """
    def get(self, request):
        logger.info(f"[IndexIdConfigListView] 开始查询INDEXID配置列表，请求路径: {request.path}")
        try:
            configs = IndexIdConfig.objects.all()
            logger.info(f"[IndexIdConfigListView] INDEXID配置查询完成，记录数: {configs.count()}")
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            
            context = {
                'configs': configs,
                'is_editable': is_editable,
            }
            logger.info(f"[IndexIdConfigListView] INDEXID配置列表查询成功，即将渲染模板")
            return render(request, 'parameter/indexid_configs.html', context)
        except Exception as e:
            logger.error(f"[IndexIdConfigListView] INDEXID配置列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class IndexIdConfigCreateView(View):
    """
    INDEXID配置创建视图
    仅管理员和技术人员可访问，用于创建新的INDEXID配置
    
    创建INDEXID时会自动生成物理表名，规则：根据大小写区分词并增加下划线，转换为大写
    示例：archTech -> ARCH_TECH
    """
    def get(self, request):
        logger.info(f"[IndexIdConfigCreateView] 加载创建INDEXID配置页面")
        context = {}
        return render(request, 'parameter/indexid_config_create.html', context)
    
    def post(self, request):
        logger.info(f"[IndexIdConfigCreateView] 创建INDEXID配置")
        try:
            config = IndexIdConfig(
                index_id=request.POST.get('index_id'),
                business_name=request.POST.get('business_name'),
                business_description=request.POST.get('business_description'),
            )
            config.save()
            logger.info(f"[IndexIdConfigCreateView] INDEXID配置创建成功，index_id: {config.index_id}, table_name: {config.table_name}")
            return redirect('index_id_config_list')
        except Exception as e:
            logger.error(f"[IndexIdConfigCreateView] 创建INDEXID配置失败: {str(e)}", exc_info=True)
            context = {
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/indexid_config_create.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class IndexIdConfigEditView(View):
    """
    INDEXID配置编辑视图
    仅管理员和技术人员可访问，用于修改INDEXID配置
    """
    def get(self, request, config_id):
        logger.info(f"[IndexIdConfigEditView] 加载编辑INDEXID配置页面，config_id: {config_id}")
        try:
            config = IndexIdConfig.objects.get(id=config_id)
            context = {
                'config': config,
            }
            return render(request, 'parameter/indexid_config_edit.html', context)
        except IndexIdConfig.DoesNotExist:
            logger.error(f"[IndexIdConfigEditView] INDEXID配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': 'INDEXID配置不存在'})
    
    def post(self, request, config_id):
        logger.info(f"[IndexIdConfigEditView] 更新INDEXID配置，config_id: {config_id}")
        try:
            config = IndexIdConfig.objects.get(id=config_id)
            config.index_id = request.POST.get('index_id')
            config.business_name = request.POST.get('business_name')
            config.business_description = request.POST.get('business_description')
            config.save()
            logger.info(f"[IndexIdConfigEditView] INDEXID配置更新成功，index_id: {config.index_id}, table_name: {config.table_name}")
            return redirect('index_id_config_list')
        except IndexIdConfig.DoesNotExist:
            logger.error(f"[IndexIdConfigEditView] INDEXID配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': 'INDEXID配置不存在'})
        except Exception as e:
            logger.error(f"[IndexIdConfigEditView] 更新INDEXID配置失败: {str(e)}", exc_info=True)
            config = IndexIdConfig.objects.get(id=config_id)
            context = {
                'config': config,
                'error': str(e),
            }
            return render(request, 'parameter/indexid_config_edit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class IndexIdConfigDeleteView(View):
    """
    INDEXID配置删除视图
    仅管理员和技术人员可访问，用于删除INDEXID配置
    """
    def get(self, request, config_id):
        logger.info(f"[IndexIdConfigDeleteView] 删除INDEXID配置，config_id: {config_id}")
        try:
            config = IndexIdConfig.objects.get(id=config_id)
            config.delete()
            logger.info(f"[IndexIdConfigDeleteView] INDEXID配置删除成功，index_id: {config.index_id}")
            return redirect('index_id_config_list')
        except IndexIdConfig.DoesNotExist:
            logger.error(f"[IndexIdConfigDeleteView] INDEXID配置不存在，config_id: {config_id}")
            return render(request, 'parameter/error.html', {'message': 'INDEXID配置不存在'})
