"""
需求视图模块
提供业务需求的列表、详情、创建、编辑、删除和流转功能
支持ZIP导出和CSV导入功能
"""
import logging
import csv
import io
import zipfile
import json
import hashlib
from datetime import datetime

from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpResponse

from ..auth_views import login_required, admin_required, role_required
from ..models import Requirement, ParameterTable, RequirementFieldConfig, FieldDefinition, Metadata
from ..utils.pagination import paginate_queryset

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class RequirementListView(View):
    """
    需求列表视图
    展示业务需求登记列表，支持按状态和类型筛选
    根据用户角色显示不同操作按钮
    """
    def get(self, request):
        logger.info(f"[RequirementListView] 开始查询需求列表，请求路径: {request.path}")
        try:
            requirements = Requirement.objects.all().order_by('-request_date')
            logger.info(f"[RequirementListView] 需求查询完成，记录数: {requirements.count()}")
            
            status_filter = request.GET.get('status', '')
            type_filter = request.GET.get('type', '')
            logger.info(f"[RequirementListView] 查询条件 - status: '{status_filter}', type: '{type_filter}'")
            
            if status_filter:
                requirements = requirements.filter(status=status_filter)
                logger.info(f"[RequirementListView] 按状态过滤后记录数: {requirements.count()}")
            
            if type_filter:
                requirements = requirements.filter(requirement_type=type_filter)
                logger.info(f"[RequirementListView] 按类型过滤后记录数: {requirements.count()}")
            
            search_name = request.GET.get('search', '')
            if search_name:
                requirements = requirements.filter(title__icontains=search_name) | requirements.filter(requirement_no__icontains=search_name) | requirements.filter(business_description__icontains=search_name) | requirements.filter(requester__icontains=search_name)
                logger.info(f"[RequirementListView] 搜索后记录数: {requirements.count()}")
            
            role_code = request.user.role.role_code
            is_editable = role_code in ['admin', 'technical', 'business']
            is_business = role_code in ['admin', 'business']
            is_technical = role_code in ['admin', 'technical']
            
            pagination, requirements = paginate_queryset(request, requirements)
            
            context = {
                'requirements': requirements,
                'status_filter': status_filter,
                'type_filter': type_filter,
                'search_name': search_name,
                'statuses': Requirement.STATUS_CHOICES,
                'types': Requirement.REQUIREMENT_TYPE_CHOICES,
                'is_editable': is_editable,
                'is_business': is_business,
                'is_technical': is_technical,
                'pagination': pagination,
            }
            logger.info(f"[RequirementListView] 需求列表查询成功，即将渲染模板")
            return render(request, 'parameter/requirement_list.html', context)
        except Exception as e:
            logger.error(f"[RequirementListView] 需求列表查询失败: {str(e)}", exc_info=True)
            raise


@method_decorator(login_required, name='dispatch')
class RequirementDetailView(View):
    """
    需求详情视图
    展示业务需求的详细信息
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementDetailView] 开始查询需求详情，req_id: {req_id}")
        try:
            requirement = Requirement.objects.filter(id=req_id).first()
            logger.info(f"[RequirementDetailView] 需求查询结果: {'存在' if requirement else '不存在'}, req_id: {req_id}")
            
            is_business = request.user.role.role_code in ['admin', 'business']
            
            context = {'requirement': requirement, 'is_business': is_business}
            logger.info(f"[RequirementDetailView] 需求详情查询成功，即将渲染模板")
            return render(request, 'parameter/requirement_detail.html', context)
        except Exception as e:
            logger.error(f"[RequirementDetailView] 需求详情查询失败，req_id: {req_id}, 错误: {str(e)}", exc_info=True)
            raise


@method_decorator(login_required, name='dispatch')
class RequirementCreateView(View):
    """
    需求创建视图
    创建新的业务需求，申请人自动填充当前登录用户的姓名或账号
    """
    def get(self, request):
        logger.info(f"[RequirementCreateView] 加载创建需求页面")
        tables = ParameterTable.objects.all()
        requester_name = request.user.real_name if request.user.real_name else request.user.username
        context = {
            'tables': tables,
            'requester_name': requester_name,
            'types': Requirement.REQUIREMENT_TYPE_CHOICES,
        }
        return render(request, 'parameter/requirement_create.html', context)
    
    def post(self, request):
        logger.info(f"[RequirementCreateView] 创建需求")
        try:
            requester_name = request.user.real_name if request.user.real_name else request.user.username
            
            requirement = Requirement(
                requirement_no=request.POST.get('requirement_no'),
                title=request.POST.get('title'),
                requirement_type=request.POST.get('requirement_type'),
                parameter_table_id=request.POST.get('parameter_table') or None,
                business_description=request.POST.get('business_description'),
                requester=requester_name,
                status='pending',
                flow_status='draft',
            )
            requirement.save()
            logger.info(f"[RequirementCreateView] 需求创建成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Exception as e:
            logger.error(f"[RequirementCreateView] 创建需求失败: {str(e)}", exc_info=True)
            tables = ParameterTable.objects.all()
            context = {
                'tables': tables,
                'requester_name': request.user.real_name if request.user.real_name else request.user.username,
                'types': Requirement.REQUIREMENT_TYPE_CHOICES,
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/requirement_create.html', context)


@method_decorator(role_required(['admin', 'technical', 'business']), name='dispatch')
class RequirementEditView(View):
    """
    需求编辑视图
    管理员、技术人员、业务人员可编辑需求
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementEditView] 加载编辑需求页面，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            tables = ParameterTable.objects.all()
            context = {
                'requirement': requirement,
                'tables': tables,
                'types': Requirement.REQUIREMENT_TYPE_CHOICES,
                'statuses': Requirement.STATUS_CHOICES,
            }
            return render(request, 'parameter/requirement_edit.html', context)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementEditView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
    
    def post(self, request, req_id):
        logger.info(f"[RequirementEditView] 更新需求，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            requirement.requirement_no = request.POST.get('requirement_no')
            requirement.title = request.POST.get('title')
            requirement.requirement_type = request.POST.get('requirement_type')
            requirement.parameter_table_id = request.POST.get('parameter_table') or None
            requirement.business_description = request.POST.get('business_description')
            requirement.status = request.POST.get('status')
            requirement.story_points = request.POST.get('story_points') or None
            requirement.sprint = request.POST.get('sprint')
            requirement.project_platform_id = request.POST.get('project_platform_id')
            requirement.save()
            logger.info(f"[RequirementEditView] 需求更新成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementEditView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except Exception as e:
            logger.error(f"[RequirementEditView] 更新需求失败: {str(e)}", exc_info=True)
            requirement = Requirement.objects.get(id=req_id)
            tables = ParameterTable.objects.all()
            context = {
                'requirement': requirement,
                'tables': tables,
                'types': Requirement.REQUIREMENT_TYPE_CHOICES,
                'statuses': Requirement.STATUS_CHOICES,
                'error': str(e),
            }
            return render(request, 'parameter/requirement_edit.html', context)


@method_decorator(role_required(['admin', 'technical', 'business']), name='dispatch')
class RequirementDeleteView(View):
    """
    需求删除视图
    业务人员只能删除草稿状态的需求，已提交的不能删除
    管理员和技术人员可以删除所有需求
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementDeleteView] 删除需求，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            
            if request.user.role.role_code == 'business' and requirement.flow_status != 'draft':
                logger.warning(f"[RequirementDeleteView] 业务人员不能删除已流转的需求，req_id: {req_id}, flow_status: {requirement.flow_status}")
                return render(request, 'parameter/error.html', {'message': '已流转的需求不可删除'})
            
            requirement.delete()
            logger.info(f"[RequirementDeleteView] 需求删除成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementDeleteView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementSubmitView(View):
    """
    需求提交流转视图
    业务人员可以将需求提交给技术人员处理
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementSubmitView] 加载提交需求页面，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            context = {'requirement': requirement}
            return render(request, 'parameter/requirement_submit.html', context)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementSubmitView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
    
    def post(self, request, req_id):
        logger.info(f"[RequirementSubmitView] 提交需求，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            requirement.flow_status = 'submitted'
            requirement.assignee = request.POST.get('assignee')
            requirement.flow_time = timezone.now()
            requirement.flow_comment = request.POST.get('flow_comment')
            requirement.status = 'approved'
            requirement.save()
            logger.info(f"[RequirementSubmitView] 需求提交成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementSubmitView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except Exception as e:
            logger.error(f"[RequirementSubmitView] 提交需求失败: {str(e)}", exc_info=True)
            requirement = Requirement.objects.get(id=req_id)
            context = {
                'requirement': requirement,
                'error': str(e),
            }
            return render(request, 'parameter/requirement_submit.html', context)


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class RequirementProcessView(View):
    """
    需求处理视图
    技术人员可以接受需求并开始处理
    """
    def post(self, request, req_id):
        logger.info(f"[RequirementProcessView] 处理需求，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            requirement.flow_status = 'processed'
            requirement.assignee = request.user.real_name if request.user.real_name else request.user.username
            requirement.status = 'in_progress'
            requirement.save()
            logger.info(f"[RequirementProcessView] 需求处理成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementProcessView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class RequirementCompleteView(View):
    """
    需求完成视图
    技术人员可以标记需求已完成
    """
    def post(self, request, req_id):
        logger.info(f"[RequirementCompleteView] 完成需求，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            requirement.flow_status = 'done'
            requirement.status = 'completed'
            requirement.save()
            logger.info(f"[RequirementCompleteView] 需求完成成功，requirement_no: {requirement.requirement_no}")
            return redirect('requirements')
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementCompleteView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})


@method_decorator(admin_required, name='dispatch')
class RequirementUpdateStatusView(View):
    """
    需求状态更新视图
    仅管理员可访问，用于更新需求状态
    """
    def post(self, request, req_id):
        logger.info(f"[RequirementUpdateStatusView] 更新需求状态，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            new_status = request.POST.get('status')
            requirement.status = new_status
            requirement.save()
            logger.info(f"[RequirementUpdateStatusView] 需求状态更新成功，requirement_no: {requirement.requirement_no}, status: {new_status}")
            return redirect('requirement_detail', req_id=req_id)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementUpdateStatusView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except Exception as e:
            logger.error(f"[RequirementUpdateStatusView] 更新需求状态失败: {str(e)}", exc_info=True)
            raise


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementExportView(View):
    """
    需求ZIP导出视图
    业务人员和管理员可以导出需求为ZIP文件，包含多个文件
    文件格式：requirements_datetime.zip
    ZIP内容：
    - requirement.csv - 需求基本信息
    - {table_name}.csv - 各参数表的字段配置（按表名命名）
    - version_hash - 版本哈希文件，用于验证导入版本
    """
    def get(self, request):
        logger.info(f"[RequirementExportView] 业务人员导出需求ZIP")
        try:
            ids_param = request.GET.get('ids')
            if ids_param:
                ids = [int(id.strip()) for id in ids_param.split(',') if id.strip().isdigit()]
                requirements = Requirement.objects.filter(id__in=ids).order_by('-request_date')
            else:
                requirements = Requirement.objects.all().order_by('-request_date')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'requirements_{timestamp}.zip'
            
            zip_buffer = io.BytesIO()
            
            file_contents = {}
            
            requirement_csv = io.StringIO()
            writer = csv.writer(requirement_csv)
            writer.writerow(['需求编号', '需求标题', '需求类型', '关联参数表', '业务说明', '申请人', '状态', '流转状态', '申请日期'])
            
            for req in requirements:
                table_name = req.parameter_table.name if req.parameter_table else ''
                req_type = dict(Requirement.REQUIREMENT_TYPE_CHOICES).get(req.requirement_type, req.requirement_type)
                status = dict(Requirement.STATUS_CHOICES).get(req.status, req.status)
                flow_status = dict(Requirement.FLOW_STATUS_CHOICES).get(req.flow_status, req.flow_status)
                
                writer.writerow([
                    req.requirement_no,
                    req.title,
                    req_type,
                    table_name,
                    req.business_description,
                    req.requester,
                    status,
                    flow_status,
                    req.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                ])
            file_contents['requirement.csv'] = requirement_csv.getvalue()
            
            tables_with_fields = {}
            for req in requirements:
                if req.parameter_table:
                    table_id = req.parameter_table.id
                    if table_id not in tables_with_fields:
                        tables_with_fields[table_id] = {
                            'table': req.parameter_table,
                            'field_configs': [],
                        }
                    field_configs = RequirementFieldConfig.objects.filter(requirement_id=req.id).order_by('sort_order')
                    tables_with_fields[table_id]['field_configs'].extend([(req, fc) for fc in field_configs])
            
            for table_id, data in tables_with_fields.items():
                table = data['table']
                safe_table_name = self._safe_filename(table.name_en)
                table_csv = io.StringIO()
                writer = csv.writer(table_csv)
                writer.writerow(['需求编号', '字段名', '显示名称', '字段类型', '长度', '小数位数', '前端控件类型', '存储方式', '是否必填', '校验规则', '排序号'])
                
                for req, field in data['field_configs']:
                    writer.writerow([
                        req.requirement_no,
                        field.field_name,
                        field.display_name,
                        field.field_type,
                        field.length or '',
                        field.decimal_places or '',
                        field.control_type,
                        field.storage_type,
                        '是' if field.is_required else '否',
                        field.validation_rule or '',
                        field.sort_order,
                    ])
                file_contents[f'{safe_table_name}.csv'] = table_csv.getvalue()
            
            all_content = json.dumps(file_contents, ensure_ascii=False, sort_keys=True)
            version_hash = hashlib.md5(all_content.encode('utf-8')).hexdigest()
            file_contents['version_hash'] = version_hash
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, content in file_contents.items():
                    zip_file.writestr(file_name, content.encode('utf-8-sig') if file_name.endswith('.csv') else content.encode('utf-8'))
            
            zip_buffer.seek(0)
            
            request.session['last_export_version_hash'] = version_hash
            
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"[RequirementExportView] 需求ZIP导出成功，记录数: {requirements.count()}, 文件名: {filename}, version_hash: {version_hash}")
            return response
        except Exception as e:
            logger.error(f"[RequirementExportView] 导出需求ZIP失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': '导出失败'})
    
    def _safe_filename(self, name):
        import re
        name = re.sub(r'[\\/:*?"<>|]', '_', name)
        name = re.sub(r'\s+', '_', name)
        return name[:100]


class BaseZIPImportView(View):
    """
    ZIP导入基类视图
    提供通用的ZIP文件导入逻辑，通过多态方法实现不同导入类型的差异化处理
    支持根据ZIP文件内容自动检测导入类型
    """
    
    IMPORT_TYPES = {
        'requirement.csv': 'standard',
        'requirement_response.csv': 'response',
    }
    
    import_template = ''
    
    def _get_import_template(self):
        return self.import_template
    
    def _detect_import_type(self, file_list):
        """
        根据ZIP文件内容自动检测导入类型
        """
        for csv_file, import_type in self.IMPORT_TYPES.items():
            if csv_file in file_list:
                return import_type, csv_file
        return None, None
    
    def _parse_csv_row(self, row, import_type):
        """
        解析CSV行数据，根据导入类型实现不同的解析逻辑
        """
        raise NotImplementedError
    
    def _get_additional_files(self, zf, file_list, import_type):
        """
        获取ZIP中的额外文件数据，子类可重写此方法
        """
        return {}
    
    def _process_imported_data(self, request, imported_data, additional_data, version_hash, import_type):
        """
        处理导入的数据，根据导入类型实现不同的处理逻辑
        """
        raise NotImplementedError
    
    def get(self, request):
        logger.info(f"[{self.__class__.__name__}] 加载导入页面")
        return render(request, self._get_import_template())
    
    def post(self, request):
        logger.info(f"[{self.__class__.__name__}] 开始导入ZIP")
        try:
            zip_file = request.FILES.get('zip_file')
            if not zip_file:
                return render(request, self._get_import_template(), {'error': '请选择ZIP文件'})
            
            zip_data = zip_file.read()
            zip_buffer = io.BytesIO(zip_data)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                file_list = zf.namelist()
                
                if 'version_hash' not in file_list:
                    return render(request, self._get_import_template(), {'error': 'ZIP文件中缺少version_hash文件，请重新导出'})
                
                import_type, required_file = self._detect_import_type(file_list)
                if import_type is None:
                    return render(request, self._get_import_template(), {'error': '无法识别ZIP文件类型，请确保上传正确的需求或反馈ZIP文件'})
                
                version_hash = zf.read('version_hash').decode('utf-8').strip()
                
                last_export_hash = request.session.get('last_export_version_hash')
                if not last_export_hash:
                    return render(request, self._get_import_template(), {'error': '未找到对应的导出版本，请先导出需求'})
                
                if version_hash != last_export_hash:
                    return render(request, self._get_import_template(), {'error': f'版本不匹配，当前版本: {version_hash[:8]}...，期望版本: {last_export_hash[:8]}...，请重新导出并导入'})
                
                csv_content = zf.read(required_file).decode('utf-8-sig')
                io_string = io.StringIO(csv_content)
                reader = csv.reader(io_string)
                
                headers = next(reader)
                
                imported_data = []
                for row in reader:
                    if len(row) < 8:
                        continue
                    imported_data.append(self._parse_csv_row(row, import_type))
                
                additional_data = self._get_additional_files(zf, file_list, import_type)
            
            logger.info(f"[{self.__class__.__name__}] ZIP导入成功，导入类型: {import_type}, 记录数: {len(imported_data)}, version_hash: {version_hash}")
            
            return self._process_imported_data(request, imported_data, additional_data, version_hash, import_type)
        except zipfile.BadZipFile:
            logger.error(f"[{self.__class__.__name__}] 无效的ZIP文件")
            return render(request, self._get_import_template(), {'error': '无效的ZIP文件，请确保上传的是有效的ZIP压缩包'})
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] 导入ZIP失败: {str(e)}", exc_info=True)
            return render(request, self._get_import_template(), {'error': str(e)})


@method_decorator(login_required, name='dispatch')
class RequirementZIPImportView(BaseZIPImportView):
    """
    统一的需求ZIP导入视图
    根据用户角色和上传文件类型自动判断导入方式：
    - 技术人员(technical): 导入需求ZIP进行编辑，或导入反馈ZIP进行查看
    - 业务人员(business): 导入反馈ZIP查看技术调整内容
    支持自动检测ZIP文件类型（需求文件/反馈文件）
    """
    
    import_template = 'parameter/requirement_import_unified.html'
    
    def _parse_csv_row(self, row, import_type):
        if import_type == 'standard':
            return {
                'requirement_no': row[0],
                'title': row[1],
                'requirement_type': row[2],
                'parameter_table': row[3],
                'business_description': row[4] if len(row) > 4 else '',
                'requester': row[5] if len(row) > 5 else '',
                'status': row[6] if len(row) > 6 else '',
                'flow_status': row[7] if len(row) > 7 else '',
                'request_date': row[8] if len(row) > 8 else '',
                'modified_fields': [],
                'tech_comments': '',
            }
        elif import_type == 'response':
            return {
                'requirement_no': row[0],
                'title': row[1],
                'requirement_type': row[2],
                'parameter_table': row[3],
                'business_description': row[4] if len(row) > 4 else '',
                'requester': row[5] if len(row) > 5 else '',
                'status': row[6] if len(row) > 6 else '',
                'flow_status': row[7] if len(row) > 7 else '',
                'request_date': row[8] if len(row) > 8 else '',
                'modified_fields': row[9].split(',') if len(row) > 9 and row[9] else [],
                'tech_comments': row[10] if len(row) > 10 else '',
            }
    
    def _get_additional_files(self, zf, file_list, import_type):
        if import_type == 'standard':
            field_configs_data = {}
            for file_name in file_list:
                if file_name.endswith('.csv') and file_name != 'requirement.csv':
                    table_name = file_name.replace('.csv', '')
                    csv_content = zf.read(file_name).decode('utf-8-sig')
                    field_configs_data[table_name] = csv_content
            return field_configs_data
        return {}
    
    def _process_imported_data(self, request, imported_data, additional_data, version_hash, import_type):
        role_code = request.user.role.role_code
        
        if role_code in ['admin', 'technical']:
            if import_type == 'standard':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                session_key = f'requirement_import_{timestamp}'
                request.session[session_key] = {
                    'imported_data': imported_data,
                    'field_configs_data': additional_data,
                    'version_hash': version_hash,
                }
                return render(request, 'parameter/requirement_import_edit.html', {
                    'imported_data': imported_data,
                    'import_key': session_key,
                })
            elif import_type == 'response':
                return render(request, 'parameter/requirement_response_view.html', {
                    'response_data': imported_data,
                })
        elif role_code in ['admin', 'business']:
            return render(request, 'parameter/requirement_response_view.html', {
                'response_data': imported_data,
            })
        
        return render(request, 'parameter/error.html', {'message': '无权限执行此操作'})


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class RequirementImportView(BaseZIPImportView):
    """
    需求ZIP导入视图（技术人员专用，保留兼容）
    技术人员可以导入业务人员导出的ZIP文件并进行编辑
    验证version_hash确保版本匹配
    编辑内容进行高亮标记
    """
    
    import_template = 'parameter/requirement_import.html'
    
    def _parse_csv_row(self, row, import_type):
        return {
            'requirement_no': row[0],
            'title': row[1],
            'requirement_type': row[2],
            'parameter_table': row[3],
            'business_description': row[4] if len(row) > 4 else '',
            'requester': row[5] if len(row) > 5 else '',
            'status': row[6] if len(row) > 6 else '',
            'flow_status': row[7] if len(row) > 7 else '',
            'request_date': row[8] if len(row) > 8 else '',
            'modified_fields': [],
            'tech_comments': '',
        }
    
    def _get_additional_files(self, zf, file_list, import_type):
        field_configs_data = {}
        for file_name in file_list:
            if file_name.endswith('.csv') and file_name != 'requirement.csv':
                table_name = file_name.replace('.csv', '')
                csv_content = zf.read(file_name).decode('utf-8-sig')
                field_configs_data[table_name] = csv_content
        return field_configs_data
    
    def _process_imported_data(self, request, imported_data, additional_data, version_hash, import_type):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_key = f'requirement_import_{timestamp}'
        request.session[session_key] = {
            'imported_data': imported_data,
            'field_configs_data': additional_data,
            'version_hash': version_hash,
        }
        
        return render(request, 'parameter/requirement_import_edit.html', {
            'imported_data': imported_data,
            'import_key': session_key,
        })


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class RequirementImportEditView(View):
    """
    需求ZIP导入编辑视图
    技术人员编辑导入的需求内容，标记修改字段
    """
    def post(self, request):
        logger.info(f"[RequirementImportEditView] 技术人员编辑导入的需求")
        try:
            import_key = request.POST.get('import_key')
            session_data = request.session.get(import_key, {})
            imported_data = session_data.get('imported_data', [])
            
            updated_data = []
            for i, item in enumerate(imported_data):
                prefix = f'item_{i}_'
                updated_item = {
                    'requirement_no': request.POST.get(f'{prefix}requirement_no', item['requirement_no']),
                    'title': request.POST.get(f'{prefix}title', item['title']),
                    'requirement_type': request.POST.get(f'{prefix}requirement_type', item['requirement_type']),
                    'parameter_table': request.POST.get(f'{prefix}parameter_table', item['parameter_table']),
                    'business_description': request.POST.get(f'{prefix}business_description', item['business_description']),
                    'requester': request.POST.get(f'{prefix}requester', item['requester']),
                    'status': request.POST.get(f'{prefix}status', item['status']),
                    'flow_status': request.POST.get(f'{prefix}flow_status', item['flow_status']),
                    'story_points': request.POST.get(f'{prefix}story_points', item['story_points']),
                    'sprint': request.POST.get(f'{prefix}sprint', item['sprint']),
                    'project_platform_id': request.POST.get(f'{prefix}project_platform_id', item['project_platform_id']),
                    'request_date': item['request_date'],
                    'tech_comments': request.POST.get(f'{prefix}tech_comments', ''),
                }
                
                modified_fields = []
                for field in ['requirement_no', 'title', 'requirement_type', 'parameter_table', 'business_description', 'status', 'flow_status', 'story_points', 'sprint', 'project_platform_id']:
                    if updated_item[field] != item[field]:
                        modified_fields.append(field)
                updated_item['modified_fields'] = modified_fields
                updated_data.append(updated_item)
            
            session_data['imported_data'] = updated_data
            request.session[import_key] = session_data
            
            logger.info(f"[RequirementImportEditView] 需求编辑完成，修改记录数: {len([d for d in updated_data if d['modified_fields']])}")
            
            return render(request, 'parameter/requirement_import_edit.html', {
                'imported_data': updated_data,
                'import_key': import_key,
            })
        except Exception as e:
            logger.error(f"[RequirementImportEditView] 编辑导入需求失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': '编辑失败'})


@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class RequirementExportResponseView(View):
    """
    需求反馈ZIP导出视图
    技术人员导出编辑后的需求反馈给业务人员
    文件格式：requirements_datetime_response_datetime.zip
    ZIP内容：
    - requirement_response.csv - 需求反馈（含修改标记）
    - {table_name}_response.csv - 各参数表的字段配置反馈（按表名命名）
    - version_hash - 版本哈希文件，用于验证导入版本
    """
    def get(self, request, import_key):
        logger.info(f"[RequirementExportResponseView] 技术人员导出反馈ZIP")
        try:
            session_data = request.session.get(import_key, {})
            imported_data = session_data.get('imported_data', [])
            field_configs_data = session_data.get('field_configs_data', {})
            version_hash = session_data.get('version_hash', '')
            
            if not imported_data:
                return render(request, 'parameter/error.html', {'message': '未找到导入的数据'})
            
            original_filename = ''
            for item in imported_data:
                if item.get('request_date'):
                    try:
                        dt = datetime.strptime(item['request_date'], '%Y-%m-%d %H:%M:%S')
                        original_filename = f'requirements_{dt.strftime("%Y%m%d_%H%M%S")}'
                        break
                    except:
                        pass
            
            if not original_filename:
                original_filename = f'requirements_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            
            response_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{original_filename}_response_{response_timestamp}.zip'
            
            zip_buffer = io.BytesIO()
            
            file_contents = {}
            
            response_csv = io.StringIO()
            writer = csv.writer(response_csv)
            writer.writerow(['需求编号', '需求标题', '需求类型', '关联参数表', '业务说明', '申请人', '状态', '流转状态', '申请日期', '修改字段', '技术备注'])
            
            for item in imported_data:
                modified_fields_str = ','.join(item.get('modified_fields', []))
                writer.writerow([
                    item['requirement_no'],
                    item['title'],
                    item['requirement_type'],
                    item['parameter_table'],
                    item['business_description'],
                    item['requester'],
                    item['status'],
                    item['flow_status'],
                    item['request_date'],
                    modified_fields_str,
                    item.get('tech_comments', ''),
                ])
            file_contents['requirement_response.csv'] = response_csv.getvalue()
            
            for table_name, csv_content in field_configs_data.items():
                file_contents[f'{table_name}_response.csv'] = csv_content
            
            file_contents['version_hash'] = version_hash
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, content in file_contents.items():
                    zip_file.writestr(file_name, content.encode('utf-8-sig') if file_name.endswith('.csv') else content.encode('utf-8'))
            
            zip_buffer.seek(0)
            
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"[RequirementExportResponseView] 反馈ZIP导出成功，记录数: {len(imported_data)}, 文件名: {filename}, version_hash: {version_hash}")
            return response
        except Exception as e:
            logger.error(f"[RequirementExportResponseView] 导出反馈ZIP失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': '导出失败'})


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementImportResponseView(BaseZIPImportView):
    """
    需求反馈ZIP导入视图（业务人员专用）
    业务人员导入技术人员反馈的ZIP文件，查看技术调整内容
    验证version_hash确保版本匹配
    """
    
    import_template = 'parameter/requirement_import_response.html'
    
    def _parse_csv_row(self, row, import_type):
        return {
            'requirement_no': row[0],
            'title': row[1],
            'requirement_type': row[2],
            'parameter_table': row[3],
            'business_description': row[4] if len(row) > 4 else '',
            'requester': row[5] if len(row) > 5 else '',
            'status': row[6] if len(row) > 6 else '',
            'flow_status': row[7] if len(row) > 7 else '',
            'request_date': row[8] if len(row) > 8 else '',
            'modified_fields': row[9].split(',') if len(row) > 9 and row[9] else [],
            'tech_comments': row[10] if len(row) > 10 else '',
        }
    
    def _process_imported_data(self, request, imported_data, additional_data, version_hash, import_type):
        return render(request, 'parameter/requirement_response_view.html', {
            'response_data': imported_data,
        })


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementFieldConfigView(View):
    """
    需求字段配置视图
    业务人员可以配置需求的字段，与参数表字段配置结构一致
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementFieldConfigView] 加载需求字段配置页面，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            
            field_configs = RequirementFieldConfig.objects.filter(requirement_id=req_id).order_by('sort_order')
            
            metadata_list = Metadata.objects.all()
            
            if requirement.parameter_table:
                table_fields = FieldDefinition.objects.filter(parameter_table_id=requirement.parameter_table_id).order_by('sort_order')
            else:
                table_fields = []
            
            context = {
                'requirement': requirement,
                'field_configs': field_configs,
                'metadata_list': metadata_list,
                'table_fields': table_fields,
            }
            logger.info(f"[RequirementFieldConfigView] 需求字段配置页面加载成功，字段数: {field_configs.count()}")
            return render(request, 'parameter/requirement_field_config.html', context)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementFieldConfigView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementFieldAddView(View):
    """
    需求字段添加视图
    支持从关联参数表字段复制或从元数据选择或自定义字段
    """
    def get(self, request, req_id):
        logger.info(f"[RequirementFieldAddView] 加载添加需求字段页面，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            
            metadata_list = Metadata.objects.all()
            
            if requirement.parameter_table:
                table_fields = FieldDefinition.objects.filter(parameter_table_id=requirement.parameter_table_id).order_by('sort_order')
            else:
                table_fields = []
            
            context = {
                'requirement': requirement,
                'metadata_list': metadata_list,
                'table_fields': table_fields,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
            }
            return render(request, 'parameter/requirement_field_add.html', context)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementFieldAddView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
    
    def post(self, request, req_id):
        logger.info(f"[RequirementFieldAddView] 添加需求字段，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            
            table_field_id = request.POST.get('table_field')
            metadata_id = request.POST.get('metadata')
            is_custom = request.POST.get('is_custom') == 'on'
            
            if table_field_id:
                table_field = FieldDefinition.objects.get(id=table_field_id)
                field_config = RequirementFieldConfig(
                    requirement=requirement,
                    field_definition=table_field,
                    field_name=table_field.field_name,
                    display_name=table_field.display_name,
                    field_type=table_field.field_type,
                    length=table_field.length,
                    decimal_places=table_field.decimal_places,
                    control_type=table_field.control_type,
                    storage_type=table_field.storage_type,
                    is_visible=table_field.is_visible,
                    is_required=table_field.is_required,
                    validation_rule=table_field.validation_rule,
                    sort_order=request.POST.get('sort_order', 0),
                )
            elif metadata_id and not is_custom:
                metadata = Metadata.objects.get(id=metadata_id)
                field_config = RequirementFieldConfig(
                    requirement=requirement,
                    field_name=metadata.field_name_en or metadata.name,
                    display_name=metadata.name,
                    field_type=metadata.field_type,
                    length=metadata.length,
                    decimal_places=metadata.decimal_places,
                    control_type=metadata.control_type,
                    storage_type=request.POST.get('storage_type', 'code_only'),
                    is_visible=True,
                    is_required=metadata.is_required,
                    validation_rule=metadata.validation_rule,
                    sort_order=request.POST.get('sort_order', 0),
                )
            else:
                field_config = RequirementFieldConfig(
                    requirement=requirement,
                    field_name=request.POST.get('field_name'),
                    display_name=request.POST.get('display_name'),
                    field_type=request.POST.get('field_type'),
                    length=request.POST.get('length') or None,
                    decimal_places=request.POST.get('decimal_places') or None,
                    control_type=request.POST.get('control_type'),
                    storage_type=request.POST.get('storage_type', 'code_only'),
                    is_visible=True,
                    is_required=request.POST.get('is_required') == 'on',
                    validation_rule=request.POST.get('validation_rule'),
                    sort_order=request.POST.get('sort_order', 0),
                )
            
            field_config.save()
            logger.info(f"[RequirementFieldAddView] 需求字段添加成功，field_name: {field_config.field_name}")
            return redirect('requirement_field_config', req_id=req_id)
        except Exception as e:
            logger.error(f"[RequirementFieldAddView] 添加需求字段失败: {str(e)}", exc_info=True)
            requirement = Requirement.objects.get(id=req_id)
            metadata_list = Metadata.objects.all()
            if requirement.parameter_table:
                table_fields = FieldDefinition.objects.filter(parameter_table_id=requirement.parameter_table_id).order_by('sort_order')
            else:
                table_fields = []
            context = {
                'requirement': requirement,
                'metadata_list': metadata_list,
                'table_fields': table_fields,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/requirement_field_add.html', context)


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementFieldEditView(View):
    """
    需求字段编辑视图
    编辑需求的字段配置
    """
    def get(self, request, req_id, field_id):
        logger.info(f"[RequirementFieldEditView] 加载编辑需求字段页面，req_id: {req_id}, field_id: {field_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            field_config = RequirementFieldConfig.objects.get(id=field_id)
            metadata_list = Metadata.objects.all()
            
            context = {
                'requirement': requirement,
                'field_config': field_config,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
            }
            return render(request, 'parameter/requirement_field_edit.html', context)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementFieldEditView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except RequirementFieldConfig.DoesNotExist:
            logger.error(f"[RequirementFieldEditView] 字段配置不存在，field_id: {field_id}")
            return render(request, 'parameter/error.html', {'message': '字段配置不存在'})
    
    def post(self, request, req_id, field_id):
        logger.info(f"[RequirementFieldEditView] 更新需求字段，req_id: {req_id}, field_id: {field_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            field_config = RequirementFieldConfig.objects.get(id=field_id)
            
            field_config.field_name = request.POST.get('field_name')
            field_config.display_name = request.POST.get('display_name')
            field_config.field_type = request.POST.get('field_type')
            field_config.length = request.POST.get('length') or None
            field_config.decimal_places = request.POST.get('decimal_places') or None
            field_config.control_type = request.POST.get('control_type')
            field_config.storage_type = request.POST.get('storage_type')
            field_config.is_visible = request.POST.get('is_visible') == 'on'
            field_config.is_required = request.POST.get('is_required') == 'on'
            field_config.validation_rule = request.POST.get('validation_rule')
            field_config.sort_order = request.POST.get('sort_order', 0)
            
            field_config.save()
            logger.info(f"[RequirementFieldEditView] 需求字段更新成功，field_name: {field_config.field_name}")
            return redirect('requirement_field_config', req_id=req_id)
        except Exception as e:
            logger.error(f"[RequirementFieldEditView] 更新需求字段失败: {str(e)}", exc_info=True)
            requirement = Requirement.objects.get(id=req_id)
            field_config = RequirementFieldConfig.objects.get(id=field_id)
            metadata_list = Metadata.objects.all()
            context = {
                'requirement': requirement,
                'field_config': field_config,
                'metadata_list': metadata_list,
                'field_types': [
                    ('string', '字符串'),
                    ('integer', '整数'),
                    ('decimal', '小数'),
                    ('date', '日期'),
                    ('datetime', '日期时间'),
                    ('boolean', '布尔值'),
                    ('text', '文本'),
                ],
                'control_types': [
                    ('input', '输入框'),
                    ('select', '下拉框'),
                    ('radio', '单选框'),
                    ('checkbox', '多选框'),
                    ('datepicker', '日期选择器'),
                    ('textarea', '文本域'),
                ],
                'storage_types': [
                    ('code_only', '仅存储CODE'),
                    ('code_name', '存储CODE和NAME'),
                    ('full', '完整存储'),
                ],
                'error': str(e),
            }
            return render(request, 'parameter/requirement_field_edit.html', context)


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementFieldDeleteView(View):
    """
    需求字段删除视图
    删除需求的字段配置
    """
    def get(self, request, req_id, field_id):
        logger.info(f"[RequirementFieldDeleteView] 删除需求字段，req_id: {req_id}, field_id: {field_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            field_config = RequirementFieldConfig.objects.get(id=field_id)
            field_config.delete()
            logger.info(f"[RequirementFieldDeleteView] 需求字段删除成功，field_name: {field_config.field_name}")
            return redirect('requirement_field_config', req_id=req_id)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementFieldDeleteView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except RequirementFieldConfig.DoesNotExist:
            logger.error(f"[RequirementFieldDeleteView] 字段配置不存在，field_id: {field_id}")
            return render(request, 'parameter/error.html', {'message': '字段配置不存在'})


@method_decorator(role_required(['admin', 'business']), name='dispatch')
class RequirementFieldConfirmView(View):
    """
    需求字段确认视图
    业务人员确认需求字段配置，确认后可以同步到参数表字段配置
    如果需求提出了变化，则参数清单也要对应修改（增删改）
    """
    def post(self, request, req_id):
        logger.info(f"[RequirementFieldConfirmView] 确认需求字段配置，req_id: {req_id}")
        try:
            requirement = Requirement.objects.get(id=req_id)
            
            field_configs = RequirementFieldConfig.objects.filter(requirement_id=req_id)
            for field_config in field_configs:
                field_config.is_confirmed = True
                field_config.confirmed_at = timezone.now()
                field_config.save()
            
            if requirement.parameter_table:
                requirement_field_names = set(field_configs.values_list('field_name', flat=True))
                
                for field_config in field_configs:
                    existing_field = FieldDefinition.objects.filter(
                        parameter_table_id=requirement.parameter_table_id,
                        field_name=field_config.field_name
                    ).first()
                    if existing_field:
                        existing_field.display_name = field_config.display_name
                        existing_field.field_type = field_config.field_type
                        existing_field.length = field_config.length
                        existing_field.decimal_places = field_config.decimal_places
                        existing_field.control_type = field_config.control_type
                        existing_field.storage_type = field_config.storage_type
                        existing_field.is_visible = field_config.is_visible
                        existing_field.is_required = field_config.is_required
                        existing_field.validation_rule = field_config.validation_rule
                        existing_field.sort_order = field_config.sort_order
                        existing_field.save()
                    else:
                        FieldDefinition.objects.create(
                            parameter_table=requirement.parameter_table,
                            field_name=field_config.field_name,
                            display_name=field_config.display_name,
                            field_type=field_config.field_type,
                            length=field_config.length,
                            decimal_places=field_config.decimal_places,
                            control_type=field_config.control_type,
                            storage_type=field_config.storage_type,
                            is_visible=field_config.is_visible,
                            is_required=field_config.is_required,
                            validation_rule=field_config.validation_rule,
                            sort_order=field_config.sort_order,
                        )
                
                existing_fields = FieldDefinition.objects.filter(
                    parameter_table_id=requirement.parameter_table_id
                )
                for existing_field in existing_fields:
                    if existing_field.field_name not in requirement_field_names:
                        existing_field.delete()
                        logger.info(f"[RequirementFieldConfirmView] 删除参数表中不再需要的字段: {existing_field.field_name}")
            
            logger.info(f"[RequirementFieldConfirmView] 需求字段配置确认成功，已同步到参数表")
            return redirect('requirement_field_config', req_id=req_id)
        except Requirement.DoesNotExist:
            logger.error(f"[RequirementFieldConfirmView] 需求不存在，req_id: {req_id}")
            return render(request, 'parameter/error.html', {'message': '需求不存在'})
        except Exception as e:
            logger.error(f"[RequirementFieldConfirmView] 确认需求字段配置失败: {str(e)}", exc_info=True)
            return render(request, 'parameter/error.html', {'message': '确认失败'})