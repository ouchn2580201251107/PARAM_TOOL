import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'param_tool.settings')
django.setup()

from parameter.models import Role, User
from django.contrib.auth.hashers import make_password

def init_admin():
    role_choices = [
        ('admin', '管理员', '系统管理员，拥有所有权限'),
        ('business', '业务人员', '负责需求分析和业务管理'),
        ('technical', '技术人员', '负责技术实现和测试'),
        ('general', '一般人员', '普通用户，只能查看数据'),
    ]
    
    for role_code, role_name, description in role_choices:
        role, created = Role.objects.get_or_create(role_code=role_code)
        if created:
            role.role_name = role_name
            role.description = description
            role.save()
            print(f"创建角色: {role_name}")
        else:
            print(f"角色已存在: {role_name}")
    
    admin_role = Role.objects.get(role_code='admin')
    
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.real_name = '系统管理员'
        admin_user.role = admin_role
        admin_user.is_active = True
        admin_user.set_password('admin123')
        admin_user.save()
        print("更新admin用户密码成功")
    except User.DoesNotExist:
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.real_name = '系统管理员'
        admin_user.role = admin_role
        admin_user.is_active = True
        admin_user.set_password('admin123')
        admin_user.save()
        print("创建admin用户成功")

if __name__ == '__main__':
    init_admin()