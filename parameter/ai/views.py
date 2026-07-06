"""
AI相关视图模块
提供AI分析和AI生成功能的Web界面
"""
import logging
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from parameter.auth_views import login_required
from parameter.models import ParameterTable, Requirement
from .ai_service import AIParameterTableAnalyzer, AIGeneratorService

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class AIAnalysisView(View):
    """
    AI分析页面视图
    展示参数表统一分析和字段规范性分析的入口页面
    """
    def get(self, request):
        logger.info(f"[AIAnalysisView] 加载AI分析页面")
        tables = ParameterTable.objects.all()
        
        context = {
            'tables': tables,
            'analysis_result': None,
            'table_id': ''
        }
        return render(request, 'parameter/ai_analysis.html', context)

@method_decorator(login_required, name='dispatch')
class AIUnificationAnalysisView(View):
    """
    参数表统一分析视图
    执行参数表是否适合统一到SIMPLELIST表的AI分析
    """
    def post(self, request):
        table_id = request.POST.get('table_id')
        logger.info(f"[AIUnificationAnalysisView] 执行参数表统一分析，table_id: {table_id}")
        
        result = AIParameterTableAnalyzer.analyze_unification(table_id)
        
        tables = ParameterTable.objects.all()
        context = {
            'tables': tables,
            'analysis_result': result,
            'analysis_type': 'unification',
            'table_id': table_id
        }
        return render(request, 'parameter/ai_analysis.html', context)

@method_decorator(login_required, name='dispatch')
class AINormalizationAnalysisView(View):
    """
    字段规范性分析视图
    执行参数字段定义规范性的AI分析检查
    """
    def post(self, request):
        table_id = request.POST.get('table_id')
        logger.info(f"[AINormalizationAnalysisView] 执行字段规范性分析，table_id: {table_id}")
        
        result = AIParameterTableAnalyzer.analyze_normalization(table_id)
        
        tables = ParameterTable.objects.all()
        context = {
            'tables': tables,
            'analysis_result': result,
            'analysis_type': 'normalization',
            'table_id': table_id
        }
        return render(request, 'parameter/ai_analysis.html', context)

@method_decorator(login_required, name='dispatch')
class AIGenerationView(View):
    """
    AI生成页面视图
    展示任务书生成、测试用例生成、SQL生成的入口页面
    """
    def get(self, request):
        logger.info(f"[AIGenerationView] 加载AI生成页面")
        requirements = Requirement.objects.all()
        tables = ParameterTable.objects.all()
        
        context = {
            'requirements': requirements,
            'tables': tables,
            'generation_result': None,
            'requirement_id': '',
            'table_id': '',
            'generation_type': ''
        }
        return render(request, 'parameter/ai_generation.html', context)

@method_decorator(login_required, name='dispatch')
class AITaskDocumentGenerationView(View):
    """
    任务书生成视图
    根据需求信息通过AI生成任务书文档
    """
    def post(self, request):
        requirement_id = request.POST.get('requirement_id')
        logger.info(f"[AITaskDocumentGenerationView] 生成任务书，requirement_id: {requirement_id}")
        
        result = AIGeneratorService.generate_task_document(requirement_id)
        
        requirements = Requirement.objects.all()
        tables = ParameterTable.objects.all()
        context = {
            'requirements': requirements,
            'tables': tables,
            'generation_result': result,
            'generation_type': 'task_document',
            'requirement_id': requirement_id
        }
        return render(request, 'parameter/ai_generation.html', context)

@method_decorator(login_required, name='dispatch')
class AITestCaseGenerationView(View):
    """
    测试用例生成视图
    根据需求通过AI生成测试用例（正常流程、边界条件、异常场景）
    """
    def post(self, request):
        requirement_id = request.POST.get('requirement_id')
        logger.info(f"[AITestCaseGenerationView] 生成测试用例，requirement_id: {requirement_id}")
        
        result = AIGeneratorService.generate_test_cases(requirement_id)
        
        requirements = Requirement.objects.all()
        tables = ParameterTable.objects.all()
        context = {
            'requirements': requirements,
            'tables': tables,
            'generation_result': result,
            'generation_type': 'test_case',
            'requirement_id': requirement_id
        }
        return render(request, 'parameter/ai_generation.html', context)

@method_decorator(login_required, name='dispatch')
class AISQLGenerationView(View):
    """
    SQL生成视图
    根据自然语言描述和参数表信息通过AI生成SQL语句
    """
    def post(self, request):
        table_id = request.POST.get('table_id')
        natural_query = request.POST.get('natural_query', '')
        logger.info(f"[AISQLGenerationView] 生成SQL，table_id: {table_id}, query: {natural_query[:50]}")
        
        result = AIGeneratorService.generate_sql(table_id, natural_query)
        
        requirements = Requirement.objects.all()
        tables = ParameterTable.objects.all()
        context = {
            'requirements': requirements,
            'tables': tables,
            'generation_result': result,
            'generation_type': 'sql',
            'table_id': table_id,
            'natural_query': natural_query
        }
        return render(request, 'parameter/ai_generation.html', context)