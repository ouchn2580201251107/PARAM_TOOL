import logging
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse

from parameter.models import ParameterTable, Requirement
from .ai_service import AIParameterTableAnalyzer, AIGeneratorService

logger = logging.getLogger(__name__)

class AIAnalysisView(View):
    def get(self, request):
        logger.info(f"[AIAnalysisView] 加载AI分析页面")
        tables = ParameterTable.objects.all()
        
        context = {
            'tables': tables,
            'analysis_result': None,
            'table_id': ''
        }
        return render(request, 'parameter/ai_analysis.html', context)

class AIUnificationAnalysisView(View):
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

class AINormalizationAnalysisView(View):
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

class AIGenerationView(View):
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

class AITaskDocumentGenerationView(View):
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

class AITestCaseGenerationView(View):
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

class AISQLGenerationView(View):
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