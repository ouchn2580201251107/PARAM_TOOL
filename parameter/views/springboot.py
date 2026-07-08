"""
代码生成视图模块
提供代码生成和下载功能，包括Spring Boot代码和配置脚本
"""
import logging
import io
import zipfile
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from ..auth_views import login_required
from ..models import ParameterTable, FieldDefinition
from ..utils.springboot_generator import SpringBootCodeGenerator

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class SpringBootGeneratorView(View):
    """
    代码生成视图
    根据参数表元数据生成完整的Spring Boot项目代码和配置脚本
    """
    def get(self, request):
        logger.info(f"[SpringBootGeneratorView] 加载代码生成页面")
        tables = ParameterTable.objects.all()
        context = {'tables': tables}
        return render(request, 'parameter/springboot_generator.html', context)
    
    def post(self, request):
        logger.info(f"[SpringBootGeneratorView] 开始生成代码")
        try:
            selected_tables = request.POST.getlist('tables')
            package_name = request.POST.get('package_name', 'com.example')
            module_name = request.POST.get('module_name', 'demo')
            logger.info(f"[SpringBootGeneratorView] 选择的参数表: {selected_tables}")
            
            if not selected_tables:
                logger.warning(f"[SpringBootGeneratorView] 未选择任何参数表")
                tables = ParameterTable.objects.all()
                return render(request, 'parameter/springboot_generator.html', {
                    'tables': tables,
                    'error': '请至少选择一个参数表',
                })
            
            generator = SpringBootCodeGenerator()
            files = generator.generate_project(selected_tables, package_name, module_name)
            
            request.session['generated_files'] = files
            logger.info(f"[SpringBootGeneratorView] 代码生成成功，文件数: {len(files)}")
            
            tables = ParameterTable.objects.all()
            
            return render(request, 'parameter/springboot_generator.html', {
                'tables': tables,
                'selected_tables': selected_tables,
                'package_name': package_name,
                'module_name': module_name,
                'files': files,
            })
        except Exception as e:
            logger.error(f"[SpringBootGeneratorView] 生成代码失败: {str(e)}", exc_info=True)
            tables = ParameterTable.objects.all()
            return render(request, 'parameter/springboot_generator.html', {
                'tables': tables,
                'error': str(e),
            })


@method_decorator(login_required, name='dispatch')
class SpringBootDownloadView(View):
    """
    代码下载视图
    将生成的代码打包为ZIP文件供用户下载
    """
    def get(self, request):
        logger.info(f"[SpringBootDownloadView] 开始下载代码")
        try:
            files = request.session.get('generated_files', {})
            
            if not files:
                logger.warning(f"[SpringBootDownloadView] 未找到生成的代码文件")
                return render(request, 'parameter/error.html', {'message': '未找到生成的代码文件，请先生成代码'})
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, content in files.items():
                    zip_file.writestr(file_path, content)
            
            zip_buffer.seek(0)
            
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=generated-code.zip'
            
            logger.info(f"[SpringBootDownloadView] 代码打包下载成功")
            
            return response
        except Exception as e:
            logger.error(f"[SpringBootDownloadView] 下载代码失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': f'下载失败: {str(e)}'})