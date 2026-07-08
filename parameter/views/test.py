"""
测试视图模块
提供测试用例和自动化测试结果的管理功能
"""
import logging
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from ..auth_views import login_required
from ..models import TestCase

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class TestCaseListView(View):
    """
    测试用例列表视图
    展示所有测试用例，支持按需求编号和用例类型筛选
    """
    def get(self, request):
        logger.info(f"[TestCaseListView] 开始查询测试用例列表，请求路径: {request.path}")
        try:
            cases = TestCase.objects.all().order_by('case_no')
            logger.info(f"[TestCaseListView] 测试用例查询完成，记录数: {cases.count()}")
            
            req_no_filter = request.GET.get('req_no', '')
            type_filter = request.GET.get('type', '')
            logger.info(f"[TestCaseListView] 查询条件 - req_no: '{req_no_filter}', type: '{type_filter}'")
            
            if req_no_filter:
                cases = cases.filter(requirement__requirement_no__icontains=req_no_filter)
                logger.info(f"[TestCaseListView] 按需求编号过滤后记录数: {cases.count()}")
            
            if type_filter:
                cases = cases.filter(case_type=type_filter)
                logger.info(f"[TestCaseListView] 按用例类型过滤后记录数: {cases.count()}")
            
            context = {
                'cases': cases,
                'req_no_filter': req_no_filter,
                'type_filter': type_filter,
                'types': TestCase.CASE_TYPE_CHOICES,
            }
            logger.info(f"[TestCaseListView] 测试用例列表查询成功，即将渲染模板")
            return render(request, 'parameter/test_cases.html', context)
        except Exception as e:
            logger.error(f"[TestCaseListView] 测试用例列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(login_required, name='dispatch')
class AutomationTestResultView(View):
    """
    自动化测试结果视图
    展示自动化测试的执行结果
    """
    def get(self, request):
        logger.info(f"[AutomationTestResultView] 开始查询自动化测试结果，请求路径: {request.path}")
        try:
            from ..models import AutomationTestResult
            
            results = AutomationTestResult.objects.all().order_by('-execution_date')
            logger.info(f"[AutomationTestResultView] 测试结果查询完成，记录数: {results.count()}")
            
            context = {'results': results}
            logger.info(f"[AutomationTestResultView] 测试结果查询成功，即将渲染模板")
            return render(request, 'parameter/automation_test_result.html', context)
        except Exception as e:
            logger.error(f"[AutomationTestResultView] 测试结果查询失败: {str(e)}", exc_info=True)
            raise
