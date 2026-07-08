"""
参数表核心模型模块
包含参数表、元数据、字段定义等核心业务模型
"""
from django.db import models


class ParameterTable(models.Model):
    """
    参数表业务说明底账模型
    用于管理系统中所有参数表的基础信息，包括业务说明、负责人、版本等
    
    SIMPLE表说明：
    - SIMPLE表是公用的数据库表，字段有：INDEXID、CODE、CNAME、ENAME、OTHERS等字段
    - 在参数清单中，按照INDEXID分为多个表展示
    - SIMPLE表由系统自动配置，标记为S，仅展示不可更改
    
    名称说明：
    - name_en: 英文名称，正式名称，由大写字母和下划线组成，用于程序标识
    - name: 中文名称，用于解释说明
    """
    
    TABLE_STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '启用'),
        ('deprecated', '废弃'),
    ]

    name_en = models.CharField(max_length=200, verbose_name='英文名称（正式名称）', help_text='由大写字母和下划线组成，如：USER_INFO', default='DEFAULT_TABLE')
    name = models.CharField(max_length=200, verbose_name='中文名称', help_text='用于解释说明')
    business_description = models.TextField(verbose_name='业务说明')
    domain = models.CharField(max_length=100, verbose_name='所属业务领域')
    owner = models.CharField(max_length=100, verbose_name='负责人')
    status = models.CharField(max_length=20, choices=TABLE_STATUS_CHOICES, default='draft', verbose_name='状态')
    is_simple = models.BooleanField(default=False, verbose_name='是否SIMPLE表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    version = models.IntegerField(default=1, verbose_name='版本')

    class Meta:
        verbose_name = '参数表业务说明底账'
        verbose_name_plural = '参数表业务说明底账'

    def __str__(self):
        return f"{self.name_en} ({self.name})"


class Metadata(models.Model):
    """
    元数据配置模型
    定义系统中预设的常用元数据类型，包括字段类型、控件类型、校验规则等
    管理员和技术人员可维护此表
    """
    
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

    name = models.CharField(max_length=100, verbose_name='元数据名称')
    field_name_en = models.CharField(max_length=100, null=True, blank=True, verbose_name='字段名称英文')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, verbose_name='字段类型')
    length = models.IntegerField(null=True, blank=True, verbose_name='长度')
    decimal_places = models.IntegerField(null=True, blank=True, verbose_name='小数位数')
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPE_CHOICES, verbose_name='前端控件类型')
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
    """
    字段定义模型
    定义参数表中每个字段的详细属性，支持引用元数据或自定义配置
    
    存储方式说明：
    - code_only: 仅存储代码值，适用于业务表引用参数表的场景
    - code_name: 存储代码和名称，适用于参数表自身存储或需要冗余存储名称的场景
    - full: 完整存储所有字段，适用于需要保留完整信息的场景
    """
    
    STORAGE_TYPE_CHOICES = [
        ('code_only', '仅存储CODE'),
        ('code_name', '存储CODE和NAME'),
        ('full', '完整存储'),
    ]
    
    parameter_table = models.ForeignKey('ParameterTable', on_delete=models.CASCADE, related_name='fields', verbose_name='所属参数表')
    metadata = models.ForeignKey('Metadata', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='引用元数据')
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
