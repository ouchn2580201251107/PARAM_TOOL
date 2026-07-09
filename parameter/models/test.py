"""
测试管理模型模块
包含测试用例、测试批次、自动化测试结果等测试相关模型
"""
from django.db import models


class TestCase(models.Model):
    """
    测试用例模型
    管理系统的测试用例，支持正常流程、边界条件、异常场景三种类型
    支持自动生成草稿、技术人员确认、多种查询排序
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
    parameter_table = models.ForeignKey('parameter.ParameterTable', on_delete=models.SET_NULL, null=True, blank=True, related_name='test_cases', verbose_name='关联参数表')
    case_no = models.CharField(max_length=50, verbose_name='用例编号')
    title = models.CharField(max_length=200, verbose_name='用例标题')
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, verbose_name='用例类型')
    preconditions = models.TextField(null=True, blank=True, verbose_name='前置条件')
    steps = models.TextField(verbose_name='测试步骤')
    expected_result = models.TextField(verbose_name='预期结果')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    confirmed = models.BooleanField(default=False, verbose_name='是否确认')
    confirmed_by = models.ForeignKey('parameter.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_test_cases', verbose_name='确认人')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    automated = models.BooleanField(default=False, verbose_name='是否自动化')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'

    def __str__(self):
        return f"{self.case_no} - {self.title}"


class TestBatch(models.Model):
    """
    测试批次模型
    管理测试执行批次，记录测试进度、统计信息等
    """
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
    ]

    batch_no = models.CharField(max_length=50, verbose_name='批次编号')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='批次描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    total_cases = models.IntegerField(default=0, verbose_name='用例总数')
    passed_count = models.IntegerField(default=0, verbose_name='通过数')
    failed_count = models.IntegerField(default=0, verbose_name='失败数')
    skipped_count = models.IntegerField(default=0, verbose_name='跳过数')
    current_progress = models.IntegerField(default=0, verbose_name='当前进度(%)')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.FloatField(null=True, blank=True, verbose_name='总执行时长(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '测试批次'
        verbose_name_plural = '测试批次'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_no} - {self.get_status_display()}"
    
    @property
    def pass_rate(self):
        """通过率"""
        if self.total_cases == 0:
            return 0
        return round((self.passed_count / self.total_cases) * 100, 2)


class AutomationTestResult(models.Model):
    """
    自动化测试结果模型
    记录测试用例的自动化执行结果，包括执行状态、错误信息和执行时长
    """
    
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('skipped', '跳过'),
        ('running', '执行中'),
    ]

    test_batch = models.ForeignKey('TestBatch', on_delete=models.CASCADE, related_name='test_results', null=True, blank=True, verbose_name='关联测试批次')
    test_case = models.ForeignKey('TestCase', on_delete=models.CASCADE, related_name='test_results', verbose_name='关联测试用例')
    execution_date = models.DateTimeField(auto_now_add=True, verbose_name='执行日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='执行状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    duration = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')

    class Meta:
        verbose_name = '自动化测试结果'
        verbose_name_plural = '自动化测试结果'
        ordering = ['-execution_date']

    def __str__(self):
        return f"{self.test_case.case_no} - {self.status}"
