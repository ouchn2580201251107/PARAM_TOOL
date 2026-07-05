from django.db import models
from django.utils import timezone


class ParameterTable(models.Model):
    TABLE_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '启用'),
        ('deprecated', '废弃'),
    ]

    name = models.CharField(max_length=200, verbose_name='参数表名称')
    business_description = models.TextField(verbose_name='业务说明')
    domain = models.CharField(max_length=100, verbose_name='所属业务领域')
    owner = models.CharField(max_length=100, verbose_name='负责人')
    status = models.CharField(max_length=20, choices=TABLE_STATUS_CHOICES, default='draft', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    version = models.IntegerField(default=1, verbose_name='版本')

    class Meta:
        verbose_name = '参数表业务说明底账'
        verbose_name_plural = '参数表业务说明底账'

    def __str__(self):
        return self.name


class Metadata(models.Model):
    FIELD_TYPE_CHOICES = [
        ('string', '字符串'),
        ('integer', '整数'),
        ('decimal', '小数'),
        ('date', '日期'),
        ('datetime', '日期时间'),
        ('boolean', '布尔值'),
        ('text', '文本'),
    ]

    CONTROL_TYPE_CHOICES = [
        ('input', '输入框'),
        ('select', '下拉框'),
        ('radio', '单选框'),
        ('checkbox', '多选框'),
        ('datepicker', '日期选择器'),
        ('textarea', '文本域'),
    ]

    STORAGE_TYPE_CHOICES = [
        ('code_only', '仅存储CODE'),
        ('code_name', '独立存储CODE和NAME'),
    ]

    name = models.CharField(max_length=100, verbose_name='元数据名称')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, verbose_name='字段类型')
    length = models.IntegerField(null=True, blank=True, verbose_name='长度')
    decimal_places = models.IntegerField(null=True, blank=True, verbose_name='小数位数')
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPE_CHOICES, verbose_name='前端控件类型')
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES, default='code_only', verbose_name='存储方式')
    default_value = models.CharField(max_length=200, null=True, blank=True, verbose_name='默认值')
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    validation_rule = models.CharField(max_length=500, null=True, blank=True, verbose_name='校验规则')
    description = models.TextField(null=True, blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '元数据配置'
        verbose_name_plural = '元数据配置'

    def __str__(self):
        return f"{self.name} ({self.field_type})"


class FieldDefinition(models.Model):
    parameter_table = models.ForeignKey(ParameterTable, on_delete=models.CASCADE, related_name='fields', verbose_name='所属参数表')
    metadata = models.ForeignKey(Metadata, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='引用元数据')
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
    is_custom = models.BooleanField(default=False, verbose_name='是否定制开发')
    custom_requirement = models.TextField(null=True, blank=True, verbose_name='定制化需求')

    class Meta:
        verbose_name = '字段定义'
        verbose_name_plural = '字段定义'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.parameter_table.name} - {self.field_name}"


class Requirement(models.Model):
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

    requirement_no = models.CharField(max_length=50, unique=True, verbose_name='需求编号')
    title = models.CharField(max_length=200, verbose_name='需求标题')
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPE_CHOICES, verbose_name='需求类型')
    parameter_table = models.ForeignKey(ParameterTable, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联参数表')
    business_description = models.TextField(verbose_name='业务说明')
    requester = models.CharField(max_length=100, verbose_name='申请人')
    request_date = models.DateTimeField(auto_now_add=True, verbose_name='申请日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    story_points = models.IntegerField(null=True, blank=True, verbose_name='故事点')
    sprint = models.CharField(max_length=50, null=True, blank=True, verbose_name='冲刺')
    project_platform_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='项目管理平台ID')

    class Meta:
        verbose_name = '业务需求登记'
        verbose_name_plural = '业务需求登记'

    def __str__(self):
        return f"{self.requirement_no} - {self.title}"


class TaskDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('word', 'Word'),
        ('pdf', 'PDF'),
    ]

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='task_documents', verbose_name='关联需求')
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


class ConfigScript(models.Model):
    STATUS_CHOICES = [
        ('generated', '已生成'),
        ('submitted', '已提交'),
        ('deployed', '已部署'),
        ('failed', '失败'),
    ]

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='config_scripts', verbose_name='关联需求')
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


class IndexIdConfig(models.Model):
    parameter_table = models.ForeignKey(ParameterTable, on_delete=models.CASCADE, verbose_name='关联参数表')
    index_id = models.CharField(max_length=50, unique=True, verbose_name='INDEXID')
    business_name = models.CharField(max_length=200, verbose_name='业务名称')
    business_description = models.TextField(null=True, blank=True, verbose_name='业务说明')
    custom_column_names = models.JSONField(null=True, blank=True, verbose_name='自定义列名配置')
    display_fields = models.JSONField(null=True, blank=True, verbose_name='显示字段配置')
    validation_rules = models.JSONField(null=True, blank=True, verbose_name='校验规则配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = 'INDEXID配置'
        verbose_name_plural = 'INDEXID配置'

    def __str__(self):
        return f"{self.index_id} - {self.business_name}"


class TestCase(models.Model):
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

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='test_cases', verbose_name='关联需求')
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
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('skipped', '跳过'),
    ]

    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='test_results', verbose_name='关联测试用例')
    execution_date = models.DateTimeField(auto_now_add=True, verbose_name='执行日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='执行状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    duration = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')

    class Meta:
        verbose_name = '自动化测试结果'
        verbose_name_plural = '自动化测试结果'

    def __str__(self):
        return f"{self.test_case.case_no} - {self.status}"