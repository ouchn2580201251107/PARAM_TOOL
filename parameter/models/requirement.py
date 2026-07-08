"""
需求管理模型模块
包含业务需求、任务书、配置脚本等需求相关模型
"""
from django.db import models


class Requirement(models.Model):
    """
    业务需求登记模型
    管理系统的业务需求，支持新增、变更、复用三种类型
    支持流转功能：业务人员流转到技术人员，业务人员无法删除已流转的记录
    """
    
    REQUIREMENT_TYPE_CHOICES = [
        ('new', '新增'),
        ('modify', '变更'),
        ('reuse', '复用'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已审核'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('rejected', '已拒绝'),
    ]

    FLOW_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('processed', '处理中'),
        ('done', '已完成'),
    ]

    requirement_no = models.CharField(max_length=50, unique=True, verbose_name='需求编号')
    title = models.CharField(max_length=200, verbose_name='需求标题')
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPE_CHOICES, verbose_name='需求类型')
    parameter_table = models.ForeignKey('parameter.ParameterTable', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联参数表')
    business_description = models.TextField(verbose_name='业务说明')
    requester = models.CharField(max_length=100, verbose_name='申请人')
    request_date = models.DateTimeField(auto_now_add=True, verbose_name='申请日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    story_points = models.IntegerField(null=True, blank=True, verbose_name='故事点')
    sprint = models.CharField(max_length=50, null=True, blank=True, verbose_name='冲刺')
    project_platform_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='项目管理平台ID')
    
    flow_status = models.CharField(max_length=20, choices=FLOW_STATUS_CHOICES, default='draft', verbose_name='流转状态')
    assignee = models.CharField(max_length=100, null=True, blank=True, verbose_name='处理人')
    flow_time = models.DateTimeField(null=True, blank=True, verbose_name='流转时间')
    flow_comment = models.TextField(null=True, blank=True, verbose_name='流转备注')

    class Meta:
        verbose_name = '业务需求登记'
        verbose_name_plural = '业务需求登记'

    def __str__(self):
        return f"{self.requirement_no} - {self.title}"


class TaskDocument(models.Model):
    """
    任务书管理模型
    存储根据需求生成的任务书文档，支持Word和PDF格式
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('word', 'Word'),
        ('pdf', 'PDF'),
    ]

    requirement = models.ForeignKey('Requirement', on_delete=models.CASCADE, related_name='task_documents', verbose_name='关联需求')
    document_no = models.CharField(max_length=50, verbose_name='任务书编号')
    title = models.CharField(max_length=200, verbose_name='任务书标题')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name='文档类型')
    content = models.TextField(verbose_name='任务书内容')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    exported_at = models.DateTimeField(null=True, blank=True, verbose_name='导出时间')

    class Meta:
        verbose_name = '任务书管理'
        verbose_name_plural = '任务书管理'

    def __str__(self):
        return f"{self.document_no} - {self.title}"


class RequirementFieldConfig(models.Model):
    """
    需求字段配置模型
    存储需求中每个字段的配置信息，与参数表字段配置结构一致
    参数表清单中的字段应来源于业务最终在需求登记模块确认的字段配置情况
    """
    
    STORAGE_TYPE_CHOICES = [
        ('code_only', '仅存储CODE'),
        ('code_name', '存储CODE和NAME'),
        ('full', '完整存储'),
    ]

    requirement = models.ForeignKey('Requirement', on_delete=models.CASCADE, related_name='field_configs', verbose_name='关联需求')
    field_definition = models.ForeignKey('parameter.FieldDefinition', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='引用字段定义')
    field_name = models.CharField(max_length=100, verbose_name='字段名')
    display_name = models.CharField(max_length=200, verbose_name='显示名称')
    field_type = models.CharField(max_length=20, verbose_name='字段类型')
    length = models.IntegerField(null=True, blank=True, verbose_name='长度')
    decimal_places = models.IntegerField(null=True, blank=True, verbose_name='小数位数')
    control_type = models.CharField(max_length=20, verbose_name='前端控件类型')
    storage_type = models.CharField(max_length=20, verbose_name='存储方式')
    is_visible = models.BooleanField(default=True, verbose_name='是否显示')
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    validation_rule = models.CharField(max_length=500, null=True, blank=True, verbose_name='校验规则')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    is_confirmed = models.BooleanField(default=False, verbose_name='是否确认')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')

    class Meta:
        verbose_name = '需求字段配置'
        verbose_name_plural = '需求字段配置'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.requirement.requirement_no} - {self.field_name}"


class ConfigScript(models.Model):
    """
    配置脚本模型
    存储根据需求生成的配置脚本，记录脚本的生成、提交、部署状态
    """
    
    STATUS_CHOICES = [
        ('generated', '已生成'),
        ('submitted', '已提交'),
        ('deployed', '已部署'),
        ('failed', '失败'),
    ]

    requirement = models.ForeignKey('Requirement', on_delete=models.CASCADE, related_name='config_scripts', verbose_name='关联需求')
    script_type = models.CharField(max_length=50, verbose_name='脚本类型')
    script_content = models.TextField(verbose_name='脚本内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated', verbose_name='状态')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    deployed_at = models.DateTimeField(null=True, blank=True, verbose_name='部署时间')
    environment = models.CharField(max_length=50, null=True, blank=True, verbose_name='目标环境')

    class Meta:
        verbose_name = '配置脚本'
        verbose_name_plural = '配置脚本'

    def __str__(self):
        return f"{self.script_type} - {self.requirement.requirement_no}"
