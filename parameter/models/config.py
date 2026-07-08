"""
配置模型模块
包含INDEXID配置等系统配置相关模型
"""
from django.db import models
import re


class IndexIdConfig(models.Model):
    """
    INDEXID配置模型
    管理参数表的INDEXID配置，支持自定义列名、显示字段和校验规则
    
    SIMPLE表规则：
    - 公用的数据库表为SIMPLE，字段有：INDEXID、CODE、CNAME、ENAME、OTHERS等字段
    - 实际在参数清单中，按照INDEXID分为多个表展示
    - INDEXID根据大小写区分词并增加下划线，如INDEXID配置为archTech，则物理表名为ARCH_TECH
    """
    
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
    
    @property
    def table_name(self):
        """
        根据INDEXID生成物理表名
        规则：根据大小写区分词并增加下划线，转换为大写
        示例：archTech -> ARCH_TECH
        """
        result = re.sub(r'([a-z])([A-Z])', r'\1_\2', self.index_id)
        return result.upper()
