"""
认证与授权模型模块
包含角色、用户等认证相关模型
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Role(models.Model):
    """
    角色模型
    定义系统的角色类型，包括管理员、业务人员、技术人员、一般人员
    """
    
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('business', '业务人员'),
        ('technical', '技术人员'),
        ('general', '一般人员'),
    ]

    role_code = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='角色编码')
    role_name = models.CharField(max_length=100, verbose_name='角色名称')
    description = models.TextField(null=True, blank=True, verbose_name='角色描述')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def __str__(self):
        return self.role_name


class User(models.Model):
    """
    用户模型
    系统用户管理，支持密码加密存储和角色分配
    """
    
    username = models.CharField(max_length=100, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=255, verbose_name='密码')
    real_name = models.CharField(max_length=100, verbose_name='真实姓名')
    email = models.EmailField(null=True, blank=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    role = models.ForeignKey('Role', on_delete=models.CASCADE, verbose_name='角色')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        """
        设置密码，使用Django内置哈希函数加密存储
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        验证密码，比对原始密码与存储的哈希值
        """
        return check_password(raw_password, self.password)
