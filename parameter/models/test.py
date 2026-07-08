"""
测试管理模型模块
包含测试用例、自动化测试结果等测试相关模型
"""
from django.db import models


class TestCase(models.Model):
    """
    测试用例模型
    管理系统的测试用例，支持正常流程、边界条件、异常场景三种类型
    """
    
    CASE_TYPE_CHOICES = [
        ('normal', '正常流程'),
        ('boundary', '边界条件'),
        ('exception', '异常场景'),
    ]

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('reviewed', '已评审'),
        ('automated', '已自动化'),
        ('executed', '已执行'),
    ]

    requirement = models.ForeignKey('parameter.Requirement', on_delete=models.CASCADE, related_name='test_cases', verbose_name='关联需求')
    case_no = models.CharField(max_length=50, verbose_name='用例编号')
    title = models.CharField(max_length=200, verbose_name='用例标题')
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, verbose_name='用例类型')
    preconditions = models.TextField(null=True, blank=True, verbose_name='前置条件')
    steps = models.TextField(verbose_name='测试步骤')
    expected_result = models.TextField(verbose_name='预期结果')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    automated = models.BooleanField(default=False, verbose_name='是否自动化')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'

    def __str__(self):
        return f"{self.case_no} - {self.title}"


class AutomationTestResult(models.Model):
    """
    自动化测试结果模型
    记录测试用例的自动化执行结果，包括执行状态、错误信息和执行时长
    """
    
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('skipped', '跳过'),
    ]

    test_case = models.ForeignKey('TestCase', on_delete=models.CASCADE, related_name='test_results', verbose_name='关联测试用例')
    execution_date = models.DateTimeField(auto_now_add=True, verbose_name='执行日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='执行状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    duration = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')

    class Meta:
        verbose_name = '自动化测试结果'
        verbose_name_plural = '自动化测试结果'

    def __str__(self):
        return f"{self.test_case.case_no} - {self.status}"
