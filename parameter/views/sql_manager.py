"""
SQL管理视图模块
提供SQL脚本的编辑和执行功能
"""
import logging
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import admin_required
from ..utils.sql_executor import execute_sql

logger = logging.getLogger(__name__)


@method_decorator(admin_required, name='dispatch')
class SqlManagerView(View):
    """
    SQL管理视图
    仅管理员可访问，用于管理和执行SQL脚本
    """
    def get(self, request):
        logger.info(f"[SqlManagerView] 加载SQL管理页面")
        context = {}
        return render(request, 'parameter/sql_manager.html', context)
    
    def post(self, request):
        logger.info(f"[SqlManagerView] 执行SQL脚本")
        try:
            sql = request.POST.get('sql', '')
            logger.info(f"[SqlManagerView] 接收到SQL脚本，长度: {len(sql)}")
            
            if not sql.strip():
                logger.warning(f"[SqlManagerView] SQL脚本为空")
                return render(request, 'parameter/sql_manager.html', {'error': '请输入SQL脚本'})
            
            result = execute_sql(sql)
            
            if result.get('error'):
                logger.error(f"[SqlManagerView] SQL执行失败: {result['error']}")
                return render(request, 'parameter/sql_manager.html', {
                    'sql': sql,
                    'error': result['error'],
                })
            
            logger.info(f"[SqlManagerView] SQL执行成功，影响行数: {result.get('rows_affected', 0)}")
            return render(request, 'parameter/sql_manager.html', {
                'sql': sql,
                'result': result,
            })
        except Exception as e:
            logger.error(f"[SqlManagerView] SQL管理操作失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/sql_manager.html', {'error': str(e)})
