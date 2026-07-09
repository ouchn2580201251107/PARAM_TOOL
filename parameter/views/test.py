"""
测试视图模块
提供测试用例、测试批次和自动化测试结果的管理功能
支持自动生成测试用例草稿、手动新增、多种查询排序
"""
import logging
import time
import threading
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from ..auth_views import login_required, role_required
from ..models import TestCase, TestBatch, AutomationTestResult, Requirement, ParameterTable
from ..utils.pagination import paginate_queryset

logger = logging.getLogger(__name__)


def generate_test_cases_from_table(table):
    """
    根据参数表清单的字段配置自动生成测试用例草稿
    根据字段配置生成更具体的测试用例
    """
    cases = []
    base_no = table.name_en
    
    field_configs = table.field_set.all()
    required_fields = [fc for fc in field_configs if fc.is_required]
    unique_fields = [fc for fc in field_configs if fc.validation_rule and 'unique' in fc.validation_rule.lower()]
    numeric_fields = [fc for fc in field_configs if fc.field_type in ['int', 'decimal', 'float', 'number']]
    date_fields = [fc for fc in field_configs if fc.field_type in ['date', 'datetime', 'time']]
    email_fields = [fc for fc in field_configs if fc.field_type == 'email']
    url_fields = [fc for fc in field_configs if fc.field_type == 'url']
    
    all_templates = []
    
    all_templates.extend([
        {
            'title': f'{table.name} - 参数表完整流程测试',
            'case_type': 'normal',
            'preconditions': '系统正常运行，用户已登录，具备参数表管理权限',
            'steps': f'1. 进入参数表管理页面\n2. 找到参数表"{table.name}"\n3. 查看参数表详情和字段配置\n4. 验证参数表基本信息完整\n5. 验证所有字段配置正确显示',
            'expected_result': f'参数表"{table.name}"详情正常显示，所有字段配置可见',
        },
        {
            'title': f'{table.name} - 参数表数据录入测试',
            'case_type': 'normal',
            'preconditions': '系统正常运行，已配置参数表字段',
            'steps': f'1. 进入参数表数据录入页面\n2. 填写所有字段的正常数据\n3. 验证字段输入格式正确\n4. 保存数据\n5. 验证数据保存成功',
            'expected_result': '数据录入成功，可在数据列表中查看',
        },
    ])
    
    if required_fields:
        field_names = ', '.join([fc.display_name for fc in required_fields[:3]])
        if len(required_fields) > 3:
            field_names += f' 等{len(required_fields)}个字段'
        
        all_templates.append({
            'title': f'{table.name} - 必填字段校验测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 仅填写非必填字段\n3. 不填写必填字段（{field_names}）\n4. 点击提交按钮\n5. 验证系统校验',
            'expected_result': f'系统提示必填字段不能为空，操作被阻止',
        })
    
    if unique_fields:
        all_templates.append({
            'title': f'{table.name} - 唯一性校验测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行，已有相关数据',
            'steps': f'1. 进入参数表数据录入页面\n2. 输入与已有数据相同的唯一字段值\n3. 点击提交按钮\n4. 验证系统校验',
            'expected_result': '系统提示该值已存在，操作被阻止',
        })
    
    if numeric_fields:
        all_templates.append({
            'title': f'{table.name} - 数值类型边界测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 在数值字段中输入超出范围的值\n3. 在小数字段中输入超过精度限制的值\n4. 点击提交按钮\n5. 验证系统校验',
            'expected_result': '系统提示数值超出范围或精度超限，操作被阻止',
        })
    
    if date_fields:
        all_templates.append({
            'title': f'{table.name} - 日期字段边界测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 在日期字段输入非日期格式\n3. 在日期字段输入无效日期（如2月30日）\n4. 在日期字段输入未来日期（如果有日期范围限制）\n5. 点击提交按钮\n6. 验证系统校验',
            'expected_result': '系统正确识别日期格式错误并给出提示',
        })
    
    if email_fields:
        all_templates.append({
            'title': f'{table.name} - 邮箱格式校验测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 在邮箱字段输入非法邮箱格式（如无@符号）\n3. 在邮箱字段输入无域名的邮箱\n4. 在邮箱字段输入超长邮箱地址\n5. 点击提交按钮\n6. 验证系统校验',
            'expected_result': '系统提示邮箱格式不正确，操作被阻止',
        })
    
    if url_fields:
        all_templates.append({
            'title': f'{table.name} - URL格式校验测试',
            'case_type': 'boundary',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 在URL字段输入非法URL格式\n3. 在URL字段输入无协议的地址\n4. 在URL字段输入超长URL\n5. 点击提交按钮\n6. 验证系统校验',
            'expected_result': '系统提示URL格式不正确，操作被阻止',
        })
    
    all_templates.extend([
        {
            'title': f'{table.name} - 异常场景测试（重复提交）',
            'case_type': 'exception',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 填写完整数据\n3. 快速重复点击提交按钮\n4. 验证系统响应',
            'expected_result': '系统防止重复提交，只保存一次数据',
        },
        {
            'title': f'{table.name} - 异常场景测试（权限验证）',
            'case_type': 'exception',
            'preconditions': '使用无权限用户登录系统',
            'steps': f'1. 尝试访问参数表"{table.name}"功能\n2. 尝试执行新增/修改/删除操作\n3. 验证系统响应',
            'expected_result': '系统提示无权限，所有操作被拒绝',
        },
        {
            'title': f'{table.name} - 异常场景测试（数据格式错误）',
            'case_type': 'exception',
            'preconditions': '系统正常运行',
            'steps': f'1. 进入参数表数据录入页面\n2. 在数字字段输入非数字字符\n3. 在布尔字段输入非法值\n4. 在枚举字段输入不在选项中的值\n5. 点击提交按钮\n6. 验证系统校验',
            'expected_result': '系统正确识别格式错误并给出提示',
        },
    ])
    
    existing_nos = set(TestCase.objects.filter(parameter_table=table).values_list('case_no', flat=True))
    
    for idx, template in enumerate(all_templates):
        case_no = f'TC_{base_no}_{idx + 1:03d}'
        if case_no not in existing_nos:
            cases.append(TestCase(
                parameter_table=table,
                case_no=case_no,
                **template,
            ))
    
    return cases


@method_decorator(login_required, name='dispatch')
class TestCaseListView(View):
    """
    测试用例列表视图
    展示所有测试用例，支持多种查询排序条件
    """
    def get(self, request):
        logger.info(f"[TestCaseListView] 开始查询测试用例列表，请求路径: {request.path}")
        try:
            cases = TestCase.objects.select_related('requirement', 'parameter_table', 'confirmed_by').prefetch_related('test_results').all()
            logger.info(f"[TestCaseListView] 测试用例查询完成，记录数: {cases.count()}")
            
            req_no_filter = request.GET.get('req_no', '')
            type_filter = request.GET.get('type', '')
            status_filter = request.GET.get('status', '')
            confirmed_filter = request.GET.get('confirmed', '')
            table_name_filter = request.GET.get('table_name', '')
            sort_by = request.GET.get('sort_by', 'created_at')
            sort_order = request.GET.get('sort_order', 'desc')
            
            logger.info(f"[TestCaseListView] 查询条件 - req_no: '{req_no_filter}', type: '{type_filter}', status: '{status_filter}', confirmed: '{confirmed_filter}', table_name: '{table_name_filter}', sort_by: '{sort_by}', sort_order: '{sort_order}'")
            
            if req_no_filter:
                cases = cases.filter(requirement__requirement_no__icontains=req_no_filter)
            
            if type_filter:
                cases = cases.filter(case_type=type_filter)
            
            if status_filter:
                cases = cases.filter(status=status_filter)
            
            if confirmed_filter:
                cases = cases.filter(confirmed=(confirmed_filter == 'true'))
            
            if table_name_filter:
                cases = cases.filter(parameter_table__name_en__icontains=table_name_filter) | cases.filter(parameter_table__name__icontains=table_name_filter)
            
            sort_fields = {
                'case_no': 'case_no',
                'title': 'title',
                'status': 'status',
                'confirmed': 'confirmed',
                'created_at': 'created_at',
                'confirmed_at': 'confirmed_at',
            }
            
            sort_field = sort_fields.get(sort_by, 'created_at')
            if sort_order == 'desc':
                sort_field = f'-{sort_field}'
            cases = cases.order_by(sort_field)
            
            pagination, cases = paginate_queryset(request, cases)
            
            recent_results = {}
            for case in cases:
                results = case.test_results.order_by('-execution_date')[:5]
                recent_results[case.id] = list(results)
            
            is_technical = request.user.role.role_code in ['admin', 'technical']
            is_admin = request.user.role.role_code == 'admin'
            
            context = {
                'cases': cases,
                'req_no_filter': req_no_filter,
                'type_filter': type_filter,
                'status_filter': status_filter,
                'confirmed_filter': confirmed_filter,
                'table_name_filter': table_name_filter,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'types': TestCase.CASE_TYPE_CHOICES,
                'statuses': TestCase.STATUS_CHOICES,
                'recent_results': recent_results,
                'pagination': pagination,
                'is_technical': is_technical,
                'is_admin': is_admin,
            }
            logger.info(f"[TestCaseListView] 测试用例列表查询成功，即将渲染模板")
            return render(request, 'parameter/test_cases.html', context)
        except Exception as e:
            logger.error(f"[TestCaseListView] 测试用例列表查询失败: {str(e)}", exc_info=True)
            raise
    
    def post(self, request):
        action = request.POST.get('action')
        logger.info(f"[TestCaseListView] 执行操作: {action}")
        
        if action == 'generate_cases':
            try:
                table_id = request.POST.get('table_id')
                if not table_id:
                    return JsonResponse({'success': False, 'message': '请选择参数表'})
                
                table = ParameterTable.objects.filter(id=table_id).first()
                if not table:
                    return JsonResponse({'success': False, 'message': '参数表不存在'})
                
                new_cases = generate_test_cases_from_table(table)
                TestCase.objects.bulk_create(new_cases)
                
                logger.info(f"[TestCaseListView] 为参数表 {table.name_en} 生成了 {len(new_cases)} 条测试用例草稿")
                return JsonResponse({'success': True, 'message': f'成功生成 {len(new_cases)} 条测试用例草稿'})
            except Exception as e:
                logger.error(f"[TestCaseListView] 生成测试用例失败: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': str(e)})
        
        elif action == 'confirm_case':
            try:
                case_id = request.POST.get('case_id')
                case = get_object_or_404(TestCase, id=case_id)
                
                if request.user.role.role_code not in ['admin', 'technical']:
                    return JsonResponse({'success': False, 'message': '无权限确认测试用例'})
                
                case.confirmed = True
                case.confirmed_by = request.user
                case.confirmed_at = datetime.now()
                case.status = 'reviewed'
                case.save()
                
                logger.info(f"[TestCaseListView] 测试用例 {case.case_no} 已由 {request.user.username} 确认")
                return JsonResponse({'success': True, 'message': '测试用例已确认'})
            except Exception as e:
                logger.error(f"[TestCaseListView] 确认测试用例失败: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': str(e)})
        
        return JsonResponse({'success': False, 'message': '未知操作'})


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class TestCaseCreateView(View):
    """
    测试用例创建视图
    技术人员手动新增测试用例
    """
    def get(self, request):
        logger.info(f"[TestCaseCreateView] 进入测试用例创建页面，请求路径: {request.path}")
        try:
            requirements = Requirement.objects.filter(status__in=['approved', 'in_progress'])
            tables = ParameterTable.objects.all()
            
            context = {
                'requirements': requirements,
                'tables': tables,
                'types': TestCase.CASE_TYPE_CHOICES,
                'statuses': TestCase.STATUS_CHOICES,
            }
            return render(request, 'parameter/test_case_form.html', context)
        except Exception as e:
            logger.error(f"[TestCaseCreateView] 加载创建页面失败: {str(e)}", exc_info=True)
            raise
    
    def post(self, request):
        logger.info(f"[TestCaseCreateView] 提交测试用例创建表单")
        try:
            requirement = get_object_or_404(Requirement, id=request.POST.get('requirement'))
            
            case_no = request.POST.get('case_no')
            if not case_no:
                max_case = TestCase.objects.filter(requirement=requirement).order_by('-case_no').first()
                if max_case:
                    seq = int(max_case.case_no.split('_')[-1]) + 1
                else:
                    seq = 1
                case_no = f'TC_{requirement.requirement_no}_{seq:03d}'
            
            case = TestCase(
                requirement=requirement,
                parameter_table=ParameterTable.objects.filter(id=request.POST.get('parameter_table')).first(),
                case_no=case_no,
                title=request.POST.get('title'),
                case_type=request.POST.get('case_type'),
                preconditions=request.POST.get('preconditions'),
                steps=request.POST.get('steps'),
                expected_result=request.POST.get('expected_result'),
                status=request.POST.get('status', 'draft'),
                automated=request.POST.get('automated') == 'on',
            )
            case.save()
            
            logger.info(f"[TestCaseCreateView] 测试用例 {case.case_no} 创建成功")
            return redirect('/test-cases/')
        except Exception as e:
            logger.error(f"[TestCaseCreateView] 创建测试用例失败: {str(e)}", exc_info=True)
            requirements = Requirement.objects.filter(status__in=['approved', 'in_progress'])
            tables = ParameterTable.objects.all()
            
            context = {
                'requirements': requirements,
                'tables': tables,
                'types': TestCase.CASE_TYPE_CHOICES,
                'statuses': TestCase.STATUS_CHOICES,
                'error': str(e),
                'post_data': request.POST,
            }
            return render(request, 'parameter/test_case_form.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class TestCaseEditView(View):
    """
    测试用例编辑视图
    技术人员编辑测试用例
    """
    def get(self, request, case_id):
        logger.info(f"[TestCaseEditView] 进入测试用例编辑页面，case_id: {case_id}")
        try:
            case = get_object_or_404(TestCase, id=case_id)
            requirements = Requirement.objects.filter(status__in=['approved', 'in_progress'])
            tables = ParameterTable.objects.all()
            
            recent_results = case.test_results.order_by('-execution_date')[:10]
            
            context = {
                'case': case,
                'requirements': requirements,
                'tables': tables,
                'types': TestCase.CASE_TYPE_CHOICES,
                'statuses': TestCase.STATUS_CHOICES,
                'recent_results': recent_results,
            }
            return render(request, 'parameter/test_case_form.html', context)
        except Exception as e:
            logger.error(f"[TestCaseEditView] 加载编辑页面失败: {str(e)}", exc_info=True)
            raise
    
    def post(self, request, case_id):
        logger.info(f"[TestCaseEditView] 提交测试用例编辑表单，case_id: {case_id}")
        try:
            case = get_object_or_404(TestCase, id=case_id)
            
            case.requirement = get_object_or_404(Requirement, id=request.POST.get('requirement'))
            case.parameter_table = ParameterTable.objects.filter(id=request.POST.get('parameter_table')).first()
            case.case_no = request.POST.get('case_no')
            case.title = request.POST.get('title')
            case.case_type = request.POST.get('case_type')
            case.preconditions = request.POST.get('preconditions')
            case.steps = request.POST.get('steps')
            case.expected_result = request.POST.get('expected_result')
            case.status = request.POST.get('status')
            case.automated = request.POST.get('automated') == 'on'
            
            case.save()
            
            logger.info(f"[TestCaseEditView] 测试用例 {case.case_no} 更新成功")
            return redirect('/test-cases/')
        except Exception as e:
            logger.error(f"[TestCaseEditView] 更新测试用例失败: {str(e)}", exc_info=True)
            case = get_object_or_404(TestCase, id=case_id)
            requirements = Requirement.objects.filter(status__in=['approved', 'in_progress'])
            tables = ParameterTable.objects.all()
            
            context = {
                'case': case,
                'requirements': requirements,
                'tables': tables,
                'types': TestCase.CASE_TYPE_CHOICES,
                'statuses': TestCase.STATUS_CHOICES,
                'error': str(e),
                'post_data': request.POST,
            }
            return render(request, 'parameter/test_case_form.html', context)


def run_test_batch(batch_id):
    """
    后台执行测试批次
    """
    try:
        batch = TestBatch.objects.get(id=batch_id)
        batch.status = 'running'
        batch.start_time = datetime.now()
        batch.save()
        
        automated_cases = TestCase.objects.filter(automated=True)
        batch.total_cases = automated_cases.count()
        batch.save()
        
        executed_count = 0
        for case in automated_cases:
            result = AutomationTestResult(
                test_batch=batch,
                test_case=case,
                status='running',
            )
            result.save()
            
            time.sleep(0.5)
            
            import random
            rand = random.random()
            if rand < 0.7:
                status = 'passed'
                error_message = None
            elif rand < 0.9:
                status = 'failed'
                error_message = f"测试执行失败: {case.title}"
            else:
                status = 'skipped'
                error_message = None
            
            result.status = status
            result.error_message = error_message
            result.duration = round(random.uniform(0.1, 1.5), 2)
            result.save()
            
            if status == 'passed':
                batch.passed_count += 1
            elif status == 'failed':
                batch.failed_count += 1
            else:
                batch.skipped_count += 1
            
            executed_count += 1
            batch.current_progress = round((executed_count / batch.total_cases) * 100, 2)
            batch.save()
        
        batch.status = 'completed'
        batch.end_time = datetime.now()
        batch.duration = round((batch.end_time - batch.start_time).total_seconds(), 2)
        batch.save()
        
        logger.info(f"[run_test_batch] 测试批次执行完成，batch_no: {batch.batch_no}, 通过率: {batch.pass_rate}%")
    except Exception as e:
        logger.error(f"[run_test_batch] 测试批次执行失败: {str(e)}", exc_info=True)
        try:
            batch = TestBatch.objects.get(id=batch_id)
            batch.status = 'failed'
            batch.save()
        except:
            pass


@method_decorator(login_required, name='dispatch')
class AutomationTestResultView(View):
    """
    自动化测试结果视图
    展示自动化测试的执行结果、测试批次和执行进度
    支持按批次查看测试结果明细
    """
    def get(self, request):
        logger.info(f"[AutomationTestResultView] 开始查询自动化测试结果，请求路径: {request.path}")
        try:
            batches = TestBatch.objects.all()
            
            latest_batch = batches.first()
            
            batch_id = request.GET.get('batch_id')
            
            if batch_id:
                results_query = AutomationTestResult.objects.filter(test_batch_id=batch_id).order_by('-execution_date')
                selected_batch = TestBatch.objects.filter(id=batch_id).first()
            else:
                results_query = AutomationTestResult.objects.all().order_by('-execution_date')
                selected_batch = None
            
            total_cases = TestCase.objects.filter(automated=True).count()
            passed_count = results_query.filter(status='passed').count()
            failed_count = results_query.filter(status='failed').count()
            skipped_count = results_query.filter(status='skipped').count()
            
            results_pagination, results = paginate_queryset(request, results_query)
            
            batch_stats = []
            for batch in batches:
                batch_stats.append({
                    'batch_no': batch.batch_no,
                    'description': batch.description,
                    'status': batch.status,
                    'pass_rate': batch.pass_rate,
                    'total': batch.total_cases,
                    'passed': batch.passed_count,
                    'failed': batch.failed_count,
                    'skipped': batch.skipped_count,
                    'duration': batch.duration,
                    'created_at': batch.created_at,
                    'id': batch.id,
                })
            
            batch_stats_pagination, batch_stats = paginate_queryset(request, batch_stats, page_size=10)
            
            context = {
                'results': results,
                'batches': batches,
                'latest_batch': latest_batch,
                'total': total_cases,
                'passed': passed_count,
                'failed': failed_count,
                'skipped': skipped_count,
                'batch_stats': batch_stats,
                'selected_batch': selected_batch,
                'selected_batch_id': batch_id,
                'pagination': results_pagination,
                'batch_pagination': batch_stats_pagination,
            }
            logger.info(f"[AutomationTestResultView] 测试结果查询成功，即将渲染模板")
            return render(request, 'parameter/automation_test_result.html', context)
        except Exception as e:
            logger.error(f"[AutomationTestResultView] 测试结果查询失败: {str(e)}", exc_info=True)
            raise
    
    def post(self, request):
        action = request.POST.get('action')
        logger.info(f"[AutomationTestResultView] 执行操作: {action}")
        
        if action == 'start_test':
            try:
                batch_count = TestBatch.objects.count() + 1
                batch_no = f"BATCH_{datetime.now().strftime('%Y%m%d')}_{batch_count:03d}"
                
                batch = TestBatch(
                    batch_no=batch_no,
                    description=request.POST.get('description', ''),
                    status='pending',
                )
                batch.save()
                
                thread = threading.Thread(target=run_test_batch, args=(batch.id,))
                thread.daemon = True
                thread.start()
                
                return JsonResponse({'success': True, 'message': '测试批次已创建并开始执行', 'batch_id': batch.id})
            except Exception as e:
                logger.error(f"[AutomationTestResultView] 创建测试批次失败: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': str(e)})
        
        return JsonResponse({'success': False, 'message': '未知操作'})


@method_decorator(login_required, name='dispatch')
class TestBatchStatusView(View):
    """
    测试批次状态查询视图
    提供实时进度查询API
    """
    def get(self, request, batch_id):
        try:
            batch = TestBatch.objects.filter(id=batch_id).first()
            if not batch:
                return JsonResponse({'success': False, 'message': '批次不存在'})
            
            return JsonResponse({
                'success': True,
                'batch_no': batch.batch_no,
                'status': batch.status,
                'status_display': batch.get_status_display(),
                'total_cases': batch.total_cases,
                'passed_count': batch.passed_count,
                'failed_count': batch.failed_count,
                'skipped_count': batch.skipped_count,
                'current_progress': batch.current_progress,
                'pass_rate': batch.pass_rate,
                'start_time': batch.start_time.isoformat() if batch.start_time else None,
                'end_time': batch.end_time.isoformat() if batch.end_time else None,
                'duration': batch.duration,
            })
        except Exception as e:
            logger.error(f"[TestBatchStatusView] 查询批次状态失败: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': str(e)})
