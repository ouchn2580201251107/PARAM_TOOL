"""
首页视图模块
展示系统概览数据
"""
import logging
from django.shortcuts import render
from django.db.models import Count

from ..auth_views import login_required
from ..models import ParameterTable, Requirement, TaskDocument, ConfigScript

logger = logging.getLogger(__name__)


@login_required
def index(request):
    """
    首页视图
    展示系统概览数据，包括参数表、需求、任务书、配置脚本的统计信息
    """
    logger.info(f"[index] 开始加载首页数据，请求路径: {request.path}")
    try:
        tables = ParameterTable.objects.all()
        logger.info(f"[index] 参数表查询完成，记录数: {tables.count()}")
        
        requirements = Requirement.objects.all()
        logger.info(f"[index] 需求查询完成，记录数: {requirements.count()}")
        
        docs = TaskDocument.objects.all()
        logger.info(f"[index] 任务书查询完成，记录数: {docs.count()}")
        
        scripts = ConfigScript.objects.all()
        logger.info(f"[index] 配置脚本查询完成，记录数: {scripts.count()}")
        
        recent_requirements = requirements.order_by('-request_date')[:5]
        recent_tables = tables.order_by('-updated_at')[:5]
        
        context = {
            'tables_count': tables.count(),
            'requirements_count': requirements.count(),
            'docs_count': docs.count(),
            'scripts_count': scripts.count(),
            'recent_requirements': recent_requirements,
            'recent_tables': recent_tables,
        }
        logger.info(f"[index] 首页数据加载成功，即将渲染模板")
        return render(request, 'parameter/index.html', context)
    except Exception as e:
        logger.error(f"[index] 首页数据加载失败: {str(e)}", exc_info=True)
        raise
