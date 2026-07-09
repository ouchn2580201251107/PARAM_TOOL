"""
配置模型模块
包含INDEXID配置等系统配置相关模型
"""
from django.db import models
import re


class ProductTableConfig(models.Model):
    """
    成品表复用配置模型
    管理成品表的配置，支持多个成品表（SIMPLE、GOODS）的切换
    
    SIMPLE表规则：
    - 公用的数据库表为SIMPLE，字段有：INDEXID、CODE、CNAME、ENAME、OTHERS等字段
    - 实际在参数清单中，按照INDEXID分为多个表展示
    - INDEXID根据大小写区分词并增加下划线，如INDEXID配置为archTech，则物理表名为ARCH_TECH
    
    GOODS表规则：
    - 数据库表为GOODS，字段有：CODE1、CNAME1、ENAME1、CODE3、CNAME3、ENAME3、TAG、BEGIN_DATE、END_DATE等
    - TAG字段类似于INDEXID，用于区分不同业务配置
    """
    
    PRODUCT_TABLE_CHOICES = [
        ('SIMPLE', 'SIMPLE'),
        ('GOODS', 'GOODS'),
    ]
    
    product_table = models.CharField(max_length=20, choices=PRODUCT_TABLE_CHOICES, default='SIMPLE', verbose_name='成品表')
    index_id = models.CharField(max_length=50, verbose_name='索引标识(INDEXID/TAG)')
    business_name = models.CharField(max_length=200, verbose_name='业务名称')
    business_description = models.TextField(null=True, blank=True, verbose_name='业务说明')
    custom_column_names = models.JSONField(null=True, blank=True, verbose_name='自定义列名配置')
    display_fields = models.JSONField(null=True, blank=True, verbose_name='显示字段配置')
    validation_rules = models.JSONField(null=True, blank=True, verbose_name='校验规则配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '成品表复用配置'
        verbose_name_plural = '成品表复用配置'
        unique_together = ['product_table', 'index_id']
        db_table = 'parameter_indexidconfig'

    def __str__(self):
        return f"{self.product_table} - {self.index_id} - {self.business_name}"
    
    @property
    def table_name(self):
        """
        根据索引标识生成物理表名
        规则：根据大小写区分词并增加下划线，转换为大写
        示例：archTech -> ARCH_TECH
        """
        result = re.sub(r'([a-z])([A-Z])', r'\1_\2', self.index_id)
        return result.upper()
