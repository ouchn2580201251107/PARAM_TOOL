"""
认证与用户管理模块
提供登录、登出、用户管理、密码修改等功能，包含基于角色的权限控制装饰器
"""
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.db import connection
from django.utils.decorators import method_decorator

from .models import User, Role

logger = logging.getLogger(__name__)

def login_required(view_func):
    """
    登录验证装饰器
    验证用户是否已登录，未登录则重定向到登录页面
    """
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            logger.warning(f"[login_required] 用户未登录，重定向到登录页，请求路径: {request.path}")
            return redirect('login')
        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                del request.session['user_id']
                logger.warning(f"[login_required] 用户已禁用，重定向到登录页")
                return redirect('login')
            request.user = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist:
            del request.session['user_id']
            logger.warning(f"[login_required] 用户不存在，重定向到登录页")
            return redirect('login')
    return wrapper

def admin_required(view_func):
    """
    管理员权限验证装饰器
    验证用户是否为管理员角色，无权限则显示错误页面
    """
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        try:
            user = User.objects.get(id=user_id)
            if user.role.role_code != 'admin':
                logger.warning(f"[admin_required] 用户 {user.username} 非管理员，无权限访问")
                return render(request, 'parameter/error.html', {'message': '无权限访问此页面'})
            request.user = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist:
            return redirect('login')
    return wrapper

def role_required(allowed_roles):
    """
    角色权限验证装饰器
    验证用户角色是否在允许的角色列表中，无权限则显示错误页面
    
    Args:
        allowed_roles: 允许访问的角色编码列表，如 ['admin', 'technical']
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('login')
            try:
                user = User.objects.get(id=user_id)
                if user.role.role_code not in allowed_roles:
                    logger.warning(f"[role_required] 用户 {user.username} 角色 {user.role.role_code} 不在允许列表 {allowed_roles}")
                    return render(request, 'parameter/error.html', {'message': '无权限访问此页面'})
                request.user = user
                return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                return redirect('login')
        return wrapper
    return decorator

class LoginView(View):
    """
    用户登录视图
    提供登录页面展示和登录验证功能
    """
    def get(self, request):
        logger.info(f"[LoginView] 加载登录页面")
        return render(request, 'parameter/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.info(f"[LoginView] 用户登录尝试，用户名: {username}")
        
        if not username or not password:
            logger.warning(f"[LoginView] 用户名或密码为空")
            return render(request, 'parameter/login.html', {'error': '用户名和密码不能为空'})
        
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                logger.warning(f"[LoginView] 用户 {username} 已被禁用")
                return render(request, 'parameter/login.html', {'error': '用户已被禁用'})
            
            if user.check_password(password):
                request.session['user_id'] = user.id
                logger.info(f"[LoginView] 用户 {username} 登录成功，角色: {user.role.role_name}")
                return redirect('index')
            else:
                logger.warning(f"[LoginView] 用户 {username} 密码错误")
                return render(request, 'parameter/login.html', {'error': '用户名或密码错误'})
        except User.DoesNotExist:
            logger.warning(f"[LoginView] 用户 {username} 不存在")
            return render(request, 'parameter/login.html', {'error': '用户名或密码错误'})

class LogoutView(View):
    """
    用户登出视图
    清除用户会话并重定向到登录页面
    """
    def get(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"[LogoutView] 用户 {user.username} 退出登录")
            except User.DoesNotExist:
                pass
            del request.session['user_id']
        return redirect('login')

@method_decorator(admin_required, name='dispatch')
class UserListView(View):
    """
    用户列表视图
    仅管理员可访问，展示系统所有用户信息
    """
    def get(self, request):
        logger.info(f"[UserListView] 管理员 {request.user.username} 查看用户列表")
        users = User.objects.select_related('role').all().order_by('-created_at')
        return render(request, 'parameter/user_list.html', {'users': users, 'current_user': request.user})

@method_decorator(admin_required, name='dispatch')
class UserCreateView(View):
    """
    用户创建视图
    仅管理员可访问，用于创建新用户并分配角色
    """
    def get(self, request):
        logger.info(f"[UserCreateView] 管理员 {request.user.username} 加载创建用户页面")
        roles = Role.objects.all()
        return render(request, 'parameter/user_create.html', {'roles': roles})
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        real_name = request.POST.get('real_name')
        employee_id = request.POST.get('employee_id')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role_id = request.POST.get('role')
        
        logger.info(f"[UserCreateView] 管理员 {request.user.username} 创建用户，用户名: {username}")
        
        if not username or not password or not confirm_password or not role_id:
            roles = Role.objects.all()
            return render(request, 'parameter/user_create.html', {
                'roles': roles,
                'error': '用户名、密码和角色为必填项'
            })
        
        if password != confirm_password:
            roles = Role.objects.all()
            return render(request, 'parameter/user_create.html', {
                'roles': roles,
                'error': '两次输入的密码不一致'
            })
        
        if employee_id:
            if not employee_id.isdigit() or len(employee_id) < 5 or len(employee_id) > 7:
                roles = Role.objects.all()
                return render(request, 'parameter/user_create.html', {
                    'roles': roles,
                    'error': '工号必须为5-7位纯数字'
                })
        
        try:
            if User.objects.filter(username=username).exists():
                roles = Role.objects.all()
                return render(request, 'parameter/user_create.html', {
                    'roles': roles,
                    'error': '用户名已存在'
                })
            
            if employee_id and User.objects.filter(employee_id=employee_id).exists():
                roles = Role.objects.all()
                return render(request, 'parameter/user_create.html', {
                    'roles': roles,
                    'error': '工号已存在'
                })
            
            role = Role.objects.get(id=role_id)
            user = User(
                username=username,
                real_name=real_name,
                employee_id=employee_id,
                email=email,
                phone=phone,
                role=role
            )
            user.set_password(password)
            user.save()
            
            logger.info(f"[UserCreateView] 用户 {username} 创建成功")
            return redirect('user_list')
        except Role.DoesNotExist:
            roles = Role.objects.all()
            return render(request, 'parameter/user_create.html', {
                'roles': roles,
                'error': '角色不存在'
            })
        except Exception as e:
            logger.error(f"[UserCreateView] 创建用户失败: {str(e)}", exc_info=True)
            roles = Role.objects.all()
            return render(request, 'parameter/user_create.html', {
                'roles': roles,
                'error': '创建用户失败'
            })

@method_decorator(admin_required, name='dispatch')
class UserEditView(View):
    """
    用户编辑视图
    仅管理员可访问，用于修改用户信息和角色
    """
    def get(self, request, user_id):
        logger.info(f"[UserEditView] 管理员 {request.user.username} 编辑用户，user_id: {user_id}")
        try:
            user = User.objects.get(id=user_id)
            roles = Role.objects.all()
            return render(request, 'parameter/user_edit.html', {'user': user, 'roles': roles})
        except User.DoesNotExist:
            return render(request, 'parameter/error.html', {'message': '用户不存在'})
    
    def post(self, request, user_id):
        real_name = request.POST.get('real_name')
        employee_id = request.POST.get('employee_id')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role_id = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        logger.info(f"[UserEditView] 管理员 {request.user.username} 更新用户信息，user_id: {user_id}")
        
        if employee_id:
            if not employee_id.isdigit() or len(employee_id) < 5 or len(employee_id) > 7:
                user = User.objects.get(id=user_id)
                roles = Role.objects.all()
                return render(request, 'parameter/user_edit.html', {
                    'user': user,
                    'roles': roles,
                    'error': '工号必须为5-7位纯数字'
                })
        
        try:
            user = User.objects.get(id=user_id)
            
            if employee_id and User.objects.filter(employee_id=employee_id).exclude(id=user_id).exists():
                roles = Role.objects.all()
                return render(request, 'parameter/user_edit.html', {
                    'user': user,
                    'roles': roles,
                    'error': '工号已存在'
                })
            
            role = Role.objects.get(id=role_id)
            
            user.real_name = real_name
            user.employee_id = employee_id
            user.email = email
            user.phone = phone
            user.role = role
            user.is_active = is_active
            user.save()
            
            logger.info(f"[UserEditView] 用户 {user.username} 信息更新成功")
            return redirect('user_list')
        except (User.DoesNotExist, Role.DoesNotExist):
            return render(request, 'parameter/error.html', {'message': '用户或角色不存在'})

@method_decorator(admin_required, name='dispatch')
class UserDeleteView(View):
    """
    用户删除视图
    仅管理员可访问，用于删除用户（禁止删除当前登录的管理员）
    """
    def get(self, request, user_id):
        logger.info(f"[UserDeleteView] 管理员 {request.user.username} 删除用户，user_id: {user_id}")
        try:
            user = User.objects.get(id=user_id)
            
            if user.role.role_code == 'admin' and user.username == request.user.username:
                logger.warning(f"[UserDeleteView] 管理员尝试删除自己")
                return render(request, 'parameter/error.html', {'message': '不能删除当前登录的管理员账号'})
            
            user.delete()
            logger.info(f"[UserDeleteView] 用户 {user.username} 删除成功")
            return redirect('user_list')
        except User.DoesNotExist:
            return render(request, 'parameter/error.html', {'message': '用户不存在'})
    
    def post(self, request, user_id):
        logger.info(f"[UserDeleteView] 管理员 {request.user.username} POST删除用户，user_id: {user_id}")
        try:
            user = User.objects.get(id=user_id)
            
            if user.role.role_code == 'admin' and user.username == request.user.username:
                logger.warning(f"[UserDeleteView] 管理员尝试删除自己")
                return render(request, 'parameter/error.html', {'message': '不能删除当前登录的管理员账号'})
            
            user.delete()
            logger.info(f"[UserDeleteView] 用户 {user.username} 删除成功")
            return redirect('user_list')
        except User.DoesNotExist:
            return render(request, 'parameter/error.html', {'message': '用户不存在'})
        except Exception as e:
            logger.error(f"[UserDeleteView] 删除用户失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': f'删除用户失败: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    """
    修改密码视图
    已登录用户可修改自己的密码
    """
    def get(self, request):
        logger.info(f"[ChangePasswordView] 用户 {request.user.username} 加载修改密码页面")
        return render(request, 'parameter/change_password.html')
    
    def post(self, request):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        logger.info(f"[ChangePasswordView] 用户 {request.user.username} 修改密码")
        
        if not old_password or not new_password or not confirm_password:
            return render(request, 'parameter/change_password.html', {
                'error': '所有密码字段均为必填项'
            })
        
        if new_password != confirm_password:
            return render(request, 'parameter/change_password.html', {
                'error': '新密码两次输入不一致'
            })
        
        if not request.user.check_password(old_password):
            return render(request, 'parameter/change_password.html', {
                'error': '旧密码输入错误'
            })
        
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"[ChangePasswordView] 用户 {request.user.username} 密码修改成功")
        return render(request, 'parameter/change_password.html', {
            'success': '密码修改成功，请重新登录'
        })