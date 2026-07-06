import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Count
from django.utils.decorators import method_decorator

from .auth_views import login_required, admin_required, role_required
from .models import ParameterTable, Metadata, FieldDefinition, Requirement, TaskDocument, ConfigScript, IndexIdConfig, TestCase, AutomationTestResult

logger = logging.getLogger(__name__)

@login_required
def index(request):
    logger.info(f"[index] 开始加载首页数据，请求路径: {request.path}")
    try:
        tables = ParameterTable.objects.all()
        logger.info(f"[index] 参数表查询完成，记录数: {tables.count()}")
        
        requirements = Requirement.objects.all()
        logger.info(f"[index] 需求查询完成，记录数: {requirements.count()}")
        
        docs = TaskDocument.objects.all()
        logger.info(f"[index] 任务书查询完成，记录数: {docs.count()}")
        
        scripts = ConfigScript.objects.all()
        logger.info(f"[index] 配置脚本查询完成，记录数: {scripts.count()}")
        
        recent_requirements = requirements.order_by('-request_date')[:5]
        recent_tables = tables.order_by('-updated_at')[:5]
        
        context = {
            'tables_count': tables.count(),
            'requirements_count': requirements.count(),
            'docs_count': docs.count(),
            'scripts_count': scripts.count(),
            'recent_requirements': recent_requirements,
            'recent_tables': recent_tables,
        }
        logger.info(f"[index] 首页数据加载成功，即将渲染模板")
        return render(request, 'parameter/index.html', context)
    except Exception as e:
        logger.error(f"[index] 首页数据加载失败: {str(e)}", exc_info=True)
        raise

@method_decorator(login_required, name='dispatch')
class ParameterTableListView(View):
    def get(self, request):
        logger.info(f"[ParameterTableListView] 开始查询参数表清单，请求路径: {request.path}")
        try:
            tables = ParameterTable.objects.all()
            logger.info(f"[ParameterTableListView] 初始查询参数表记录数: {tables.count()}")
            
            domain_filter = request.GET.get('domain', '')
            status_filter = request.GET.get('status', '')
            search_name = request.GET.get('search', '')
            
            logger.info(f"[ParameterTableListView] 查询条件 - domain: '{domain_filter}', status: '{status_filter}', search: '{search_name}'")
            
            if domain_filter:
                tables = tables.filter(domain=domain_filter)
                logger.info(f"[ParameterTableListView] 按domain过滤后记录数: {tables.count()}")
            
            if status_filter:
                tables = tables.filter(status=status_filter)
                logger.info(f"[ParameterTableListView] 按status过滤后记录数: {tables.count()}")
            
            if search_name:
                tables = tables.filter(name__icontains=search_name) | tables.filter(business_description__icontains=search_name)
                logger.info(f"[ParameterTableListView] 按搜索词过滤后记录数: {tables.count()}")
            
            domains = ParameterTable.objects.values_list('domain', flat=True).distinct()
            logger.info(f"[ParameterTableListView] 获取到 {len(list(domains))} 个不同的业务领域")
            
            statuses = [{'value': 'draft', 'label': '草稿'}, {'value': 'active', 'label': '启用'}, {'value': 'deprecated', 'label': '废弃'}]
            
            context = {
                'tables': tables,
                'domains': domains,
                'statuses': statuses,
                'domain_filter': domain_filter,
                'status_filter': status_filter,
                'search_name': search_name,
            }
            logger.info(f"[ParameterTableListView] 参数表清单查询成功，即将渲染模板")
            return render(request, 'parameter/table_list.html', context)
        except Exception as e:
            logger.error(f"[ParameterTableListView] 参数表清单查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class ParameterTableDetailView(View):
    def get(self, request, table_id):
        logger.info(f"[ParameterTableDetailView] 开始查询参数表详情，table_id: {table_id}")
        try:
            table = ParameterTable.objects.filter(id=table_id).first()
            logger.info(f"[ParameterTableDetailView] 参数表查询结果: {'存在' if table else '不存在'}, table_id: {table_id}")
            
            fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            logger.info(f"[ParameterTableDetailView] 字段定义查询完成，记录数: {fields.count()}")
            
            context = {
                'table': table,
                'fields': fields,
            }
            logger.info(f"[ParameterTableDetailView] 参数表详情查询成功，即将渲染模板")
            return render(request, 'parameter/table_detail.html', context)
        except Exception as e:
            logger.error(f"[ParameterTableDetailView] 参数表详情查询失败，table_id: {table_id}, 错误: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class MetadataListView(View):
    def get(self, request):
        logger.info(f"[MetadataListView] 开始查询元数据列表，请求路径: {request.path}")
        try:
            metadata_list = Metadata.objects.all()
            logger.info(f"[MetadataListView] 元数据查询完成，记录数: {metadata_list.count()}")
            
            is_editable = request.user.role.role_code in ['admin', 'technical']
            logger.info(f"[MetadataListView] 当前用户可编辑: {is_editable}")
            
            context = {
                'metadata_list': metadata_list,
                'is_editable': is_editable,
            }
            logger.info(f"[MetadataListView] 元数据列表查询成功，即将渲染模板")
            return render(request, 'parameter/metadata_list.html', context)
        except Exception as e:
            logger.error(f"[MetadataListView] 元数据列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataCreateView(View):
    def get(self, request):
        logger.info(f"[MetadataCreateView] 加载创建元数据页面")
        context = {
            'field_types': Metadata.FIELD_TYPE_CHOICES,
            'control_types': Metadata.CONTROL_TYPE_CHOICES,
        }
        return render(request, 'parameter/metadata_create.html', context)
    
    def post(self, request):
        logger.info(f"[MetadataCreateView] 创建元数据")
        try:
            metadata = Metadata(
                name=request.POST.get('name'),
                field_type=request.POST.get('field_type'),
                length=request.POST.get('length') or None,
                decimal_places=request.POST.get('decimal_places') or None,
                control_type=request.POST.get('control_type'),
                default_value=request.POST.get('default_value'),
                is_required=request.POST.get('is_required') == 'on',
                validation_rule=request.POST.get('validation_rule'),
                description=request.POST.get('description'),
            )
            metadata.save()
            logger.info(f"[MetadataCreateView] 元数据创建成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Exception as e:
            logger.error(f"[MetadataCreateView] 创建元数据失败: {str(e)}", exc_info=True)
            context = {
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
                'error': str(e),
                'data': request.POST,
            }
            return render(request, 'parameter/metadata_create.html', context)

@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataEditView(View):
    def get(self, request, metadata_id):
        logger.info(f"[MetadataEditView] 加载编辑元数据页面，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            context = {
                'metadata': metadata,
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
            }
            return render(request, 'parameter/metadata_edit.html', context)
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataEditView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})
    
    def post(self, request, metadata_id):
        logger.info(f"[MetadataEditView] 更新元数据，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            metadata.name = request.POST.get('name')
            metadata.field_type = request.POST.get('field_type')
            metadata.length = request.POST.get('length') or None
            metadata.decimal_places = request.POST.get('decimal_places') or None
            metadata.control_type = request.POST.get('control_type')
            metadata.default_value = request.POST.get('default_value')
            metadata.is_required = request.POST.get('is_required') == 'on'
            metadata.validation_rule = request.POST.get('validation_rule')
            metadata.description = request.POST.get('description')
            metadata.save()
            logger.info(f"[MetadataEditView] 元数据更新成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataEditView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})
        except Exception as e:
            logger.error(f"[MetadataEditView] 更新元数据失败: {str(e)}", exc_info=True)
            metadata = Metadata.objects.get(id=metadata_id)
            context = {
                'metadata': metadata,
                'field_types': Metadata.FIELD_TYPE_CHOICES,
                'control_types': Metadata.CONTROL_TYPE_CHOICES,
                'error': str(e),
            }
            return render(request, 'parameter/metadata_edit.html', context)

@method_decorator(role_required(['admin', 'technical']), name='dispatch')
class MetadataDeleteView(View):
    def get(self, request, metadata_id):
        logger.info(f"[MetadataDeleteView] 删除元数据，metadata_id: {metadata_id}")
        try:
            metadata = Metadata.objects.get(id=metadata_id)
            metadata.delete()
            logger.info(f"[MetadataDeleteView] 元数据删除成功，name: {metadata.name}")
            return redirect('metadata_list')
        except Metadata.DoesNotExist:
            logger.error(f"[MetadataDeleteView] 元数据不存在，metadata_id: {metadata_id}")
            return render(request, 'parameter/error.html', {'message': '元数据不存在'})

@method_decorator(login_required, name='dispatch')
class RequirementListView(View):
    def get(self, request):
        logger.info(f"[RequirementListView] 开始查询需求列表，请求路径: {request.path}")
        try:
            requirements = Requirement.objects.all().select_related('parameter_table')
            logger.info(f"[RequirementListView] 需求查询完成，记录数: {requirements.count()}")
            
            context = {
                'requirements': requirements,
            }
            logger.info(f"[RequirementListView] 需求列表查询成功，即将渲染模板")
            return render(request, 'parameter/requirement_list.html', context)
        except Exception as e:
            logger.error(f"[RequirementListView] 需求列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class RequirementDetailView(View):
    def get(self, request, req_id):
        logger.info(f"[RequirementDetailView] 开始查询需求详情，req_id: {req_id}")
        try:
            requirement = Requirement.objects.filter(id=req_id).select_related('parameter_table').first()
            logger.info(f"[RequirementDetailView] 需求查询结果: {'存在' if requirement else '不存在'}, req_id: {req_id}")
            
            documents = TaskDocument.objects.filter(requirement_id=req_id)
            logger.info(f"[RequirementDetailView] 任务书查询完成，记录数: {documents.count()}")
            
            scripts = ConfigScript.objects.filter(requirement_id=req_id)
            logger.info(f"[RequirementDetailView] 配置脚本查询完成，记录数: {scripts.count()}")
            
            test_cases = TestCase.objects.filter(requirement_id=req_id)
            logger.info(f"[RequirementDetailView] 测试用例查询完成，记录数: {test_cases.count()}")
            
            context = {
                'requirement': requirement,
                'documents': documents,
                'scripts': scripts,
                'test_cases': test_cases,
            }
            logger.info(f"[RequirementDetailView] 需求详情查询成功，即将渲染模板")
            return render(request, 'parameter/requirement_detail.html', context)
        except Exception as e:
            logger.error(f"[RequirementDetailView] 需求详情查询失败，req_id: {req_id}, 错误: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class TaskDocumentListView(View):
    def get(self, request):
        logger.info(f"[TaskDocumentListView] 开始查询任务书列表，请求路径: {request.path}")
        try:
            documents = TaskDocument.objects.all().select_related('requirement')
            logger.info(f"[TaskDocumentListView] 任务书查询完成，记录数: {documents.count()}")
            
            context = {
                'documents': documents,
            }
            logger.info(f"[TaskDocumentListView] 任务书列表查询成功，即将渲染模板")
            return render(request, 'parameter/task_document_list.html', context)
        except Exception as e:
            logger.error(f"[TaskDocumentListView] 任务书列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class ConfigScriptListView(View):
    def get(self, request):
        logger.info(f"[ConfigScriptListView] 开始查询配置脚本列表，请求路径: {request.path}")
        try:
            scripts = ConfigScript.objects.all().select_related('requirement')
            logger.info(f"[ConfigScriptListView] 配置脚本查询完成，记录数: {scripts.count()}")
            
            context = {
                'scripts': scripts,
            }
            logger.info(f"[ConfigScriptListView] 配置脚本列表查询成功，即将渲染模板")
            return render(request, 'parameter/config_script_list.html', context)
        except Exception as e:
            logger.error(f"[ConfigScriptListView] 配置脚本列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class IndexIdConfigListView(View):
    def get(self, request):
        logger.info(f"[IndexIdConfigListView] 开始查询INDEXID配置列表，请求路径: {request.path}")
        try:
            configs = IndexIdConfig.objects.all().select_related('parameter_table')
            logger.info(f"[IndexIdConfigListView] INDEXID配置查询完成，记录数: {configs.count()}")
            
            context = {
                'configs': configs,
            }
            logger.info(f"[IndexIdConfigListView] INDEXID配置列表查询成功，即将渲染模板")
            return render(request, 'parameter/index_id_config_list.html', context)
        except Exception as e:
            logger.error(f"[IndexIdConfigListView] INDEXID配置列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class TestCaseListView(View):
    def get(self, request):
        logger.info(f"[TestCaseListView] 开始查询测试用例列表，请求路径: {request.path}")
        try:
            cases = TestCase.objects.all().select_related('requirement')
            logger.info(f"[TestCaseListView] 测试用例查询完成，记录数: {cases.count()}")
            
            context = {
                'cases': cases,
            }
            logger.info(f"[TestCaseListView] 测试用例列表查询成功，即将渲染模板")
            return render(request, 'parameter/test_case_list.html', context)
        except Exception as e:
            logger.error(f"[TestCaseListView] 测试用例列表查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class AutomationTestResultView(View):
    def get(self, request):
        logger.info(f"[AutomationTestResultView] 开始查询自动化测试结果，请求路径: {request.path}")
        try:
            results = AutomationTestResult.objects.all().select_related('test_case')
            logger.info(f"[AutomationTestResultView] 测试结果查询完成，记录数: {results.count()}")
            
            passed = results.filter(status='passed').count()
            failed = results.filter(status='failed').count()
            skipped = results.filter(status='skipped').count()
            
            logger.info(f"[AutomationTestResultView] 测试统计 - passed: {passed}, failed: {failed}, skipped: {skipped}")
            
            context = {
                'results': results,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': results.count(),
            }
            logger.info(f"[AutomationTestResultView] 自动化测试结果查询成功，即将渲染模板")
            return render(request, 'parameter/automation_test_result.html', context)
        except Exception as e:
            logger.error(f"[AutomationTestResultView] 自动化测试结果查询失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class RequirementCreateView(View):
    def get(self, request):
        logger.info(f"[RequirementCreateView] 开始加载需求创建页面，请求路径: {request.path}")
        try:
            tables = ParameterTable.objects.all()
            logger.info(f"[RequirementCreateView] 参数表查询完成，记录数: {tables.count()}")
            
            requester_name = request.user.real_name if request.user.real_name else request.user.username
            logger.info(f"[RequirementCreateView] 自动填充申请人: {requester_name}")
            
            context = {
                'tables': tables,
                'requester': requester_name,
            }
            logger.info(f"[RequirementCreateView] 需求创建页面加载成功，即将渲染模板")
            return render(request, 'parameter/requirement_create.html', context)
        except Exception as e:
            logger.error(f"[RequirementCreateView] 需求创建页面加载失败: {str(e)}", exc_info=True)
            raise

    def post(self, request):
        logger.info(f"[RequirementCreateView] 开始创建需求，请求路径: {request.path}")
        try:
            max_id = Requirement.objects.aggregate(max_id=Count('id'))['max_id'] or 0
            new_id = max_id + 1
            logger.info(f"[RequirementCreateView] 新需求ID: {new_id}")
            
            today = datetime.now().strftime('%Y-%m-%d')
            req_no = f"REQ-{today[:4]}-{str(new_id).zfill(3)}"
            logger.info(f"[RequirementCreateView] 生成需求编号: {req_no}")
            
            table_id = request.POST.get('parameter_table_id')
            table = ParameterTable.objects.filter(id=table_id).first() if table_id else None
            logger.info(f"[RequirementCreateView] 关联参数表: {table_id if table else '无'}")
            
            title = request.POST.get('title', '')
            req_type = request.POST.get('requirement_type', 'new')
            requester = request.POST.get('requester', '')
            
            logger.info(f"[RequirementCreateView] 创建需求 - 编号: {req_no}, 标题: {title}, 类型: {req_type}, 创建人: {requester}")
            
            Requirement.objects.create(
                requirement_no=req_no,
                title=title,
                requirement_type=req_type,
                parameter_table=table,
                business_description=request.POST.get('business_description', ''),
                requester=requester,
                status='pending',
                story_points=int(request.POST.get('story_points')) if request.POST.get('story_points') else None,
                sprint=request.POST.get('sprint', ''),
                project_platform_id=request.POST.get('project_platform_id', ''),
            )
            
            logger.info(f"[RequirementCreateView] 需求创建成功，需求编号: {req_no}")
            return redirect('requirement_list')
        except Exception as e:
            logger.error(f"[RequirementCreateView] 需求创建失败: {str(e)}", exc_info=True)
            raise

@method_decorator(login_required, name='dispatch')
class TaskDocumentExportView(View):
    def get(self, request, doc_id):
        logger.info(f"[TaskDocumentExportView] 开始导出任务书，doc_id: {doc_id}")
        try:
            doc = TaskDocument.objects.filter(id=doc_id).first()
            
            if not doc:
                logger.warning(f"[TaskDocumentExportView] 任务书不存在，doc_id: {doc_id}")
                return HttpResponse('任务书不存在', status=404)
            
            logger.info(f"[TaskDocumentExportView] 任务书查询成功 - 编号: {doc.document_no}, 标题: {doc.title}")
            
            response = HttpResponse(doc.content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{doc.document_no}.txt"'
            
            doc.exported_at = datetime.now()
            doc.save()
            
            logger.info(f"[TaskDocumentExportView] 任务书导出成功，已更新导出时间")
            return response
        except Exception as e:
            logger.error(f"[TaskDocumentExportView] 任务书导出失败，doc_id: {doc_id}, 错误: {str(e)}", exc_info=True)
            raise

@method_decorator(admin_required, name='dispatch')
class SpringBootGeneratorView(View):
    def get(self, request):
        tables = ParameterTable.objects.all()
        context = {
            'tables': tables,
        }
        return render(request, 'parameter/springboot_generator.html', context)

    def post(self, request):
        table_id = request.POST.get('table_id')
        package_name = request.POST.get('package_name', 'com.example')
        module_name = request.POST.get('module_name', 'demo')
        
        try:
            table = ParameterTable.objects.get(id=table_id)
            fields = FieldDefinition.objects.filter(parameter_table=table).order_by('sort_order')
            
            context = {
                'table': table,
                'fields': fields,
                'package_name': package_name,
                'module_name': module_name,
            }
            
            return render(request, 'parameter/springboot_generator.html', context)
        except ParameterTable.DoesNotExist:
            return render(request, 'parameter/springboot_generator.html', {
                'tables': ParameterTable.objects.all(),
                'error': '参数表不存在',
            })


@method_decorator(admin_required, name='dispatch')
class SpringBootDownloadView(View):
    def post(self, request):
        table_id = request.POST.get('table_id')
        package_name = request.POST.get('package_name', 'com.example')
        module_name = request.POST.get('module_name', 'demo')
        
        try:
            table = ParameterTable.objects.get(id=table_id)
            fields = FieldDefinition.objects.filter(parameter_table=table).order_by('sort_order')
            
            entity_code = self._generate_entity(table, fields, package_name, module_name)
            dto_code = self._generate_dto(table, fields, package_name, module_name)
            mapper_code = self._generate_mapper(table, package_name, module_name)
            service_code = self._generate_service(table, fields, package_name, module_name)
            service_impl_code = self._generate_service_impl(table, fields, package_name, module_name)
            controller_code = self._generate_controller(table, package_name, module_name)
            mapper_xml_code = self._generate_mapper_xml(table, fields)
            pom_code = self._generate_pom(module_name)
            application_code = self._generate_application(module_name)
            application_yaml_code = self._generate_application_yaml(package_name, module_name)
            
            import zipfile
            import io
            from django.http import HttpResponse
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/entity/{table.name.replace("代码表", "")}.java', entity_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/dto/{table.name.replace("代码表", "")}DTO.java', dto_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/mapper/{table.name.replace("代码表", "")}Mapper.java', mapper_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/service/{table.name.replace("代码表", "")}Service.java', service_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/service/impl/{table.name.replace("代码表", "")}ServiceImpl.java', service_impl_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/controller/{table.name.replace("代码表", "")}Controller.java', controller_code)
                zf.writestr(f'{module_name}/src/main/resources/mapper/{table.name.replace("代码表", "")}Mapper.xml', mapper_xml_code)
                zf.writestr(f'{module_name}/pom.xml', pom_code)
                zf.writestr(f'{module_name}/src/main/java/{package_name.replace(".", "/")}/{module_name.capitalize()}Application.java', application_code)
                zf.writestr(f'{module_name}/src/main/resources/application.yml', application_yaml_code)
            
            zip_buffer.seek(0)
            
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{module_name}-springboot.zip"'
            
            return response
        except ParameterTable.DoesNotExist:
            return HttpResponse('参数表不存在', status=400)

    def _generate_entity(self, table, fields, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        field_code = ''
        
        for field in fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            display_name = field.display_name
            is_required = '@NotBlank' if field.is_required else ''
            
            field_code += f"""
    /**
     * {display_name}
     */
    {is_required}
    private {java_type} {field_name};
"""
        
        return f"""package {package_name}.{module_name}.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * {table.name}实体类
 * {table.business_description}
 */
@Entity
@Table(name = "{table.name.replace('代码表', '').lower()}")
public class {entity_name} implements Serializable {{

    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

{field_code}
    // Getters and Setters
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
{self._generate_getters_setters(fields)}
}}
"""

    def _generate_dto(self, table, fields, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        field_code = ''
        
        for field in fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            display_name = field.display_name
            is_required = '@NotBlank' if field.is_required else ''
            
            field_code += f"""
    /**
     * {display_name}
     */
    {is_required}
    private {java_type} {field_name};
"""
        
        return f"""package {package_name}.{module_name}.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * {table.name}数据传输对象
 */
@Data
public class {entity_name}DTO {{

{field_code}
}}
"""

    def _generate_mapper(self, table, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        
        return f"""package {package_name}.{module_name}.mapper;

import {package_name}.{module_name}.entity.{entity_name};
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

/**
 * {table.name}Mapper接口
 */
@Mapper
public interface {entity_name}Mapper {{

    /**
     * 根据ID查询
     */
    {entity_name} selectById(Long id);

    /**
     * 查询所有
     */
    List<{entity_name}> selectAll();

    /**
     * 根据条件查询
     */
    List<{entity_name}> selectByCondition({entity_name} entity);

    /**
     * 新增
     */
    int insert({entity_name} entity);

    /**
     * 更新
     */
    int updateById({entity_name} entity);

    /**
     * 删除
     */
    int deleteById(Long id);
}}
"""

    def _generate_service(self, table, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        
        return f"""package {package_name}.{module_name}.service;

import {package_name}.{module_name}.dto.{entity_name}DTO;
import {package_name}.{module_name}.entity.{entity_name};
import java.util.List;

/**
 * {table.name}Service接口
 */
public interface {entity_name}Service {{

    /**
     * 根据ID查询
     */
    {entity_name} findById(Long id);

    /**
     * 查询所有
     */
    List<{entity_name}> findAll();

    /**
     * 根据条件查询
     */
    List<{entity_name}> findByCondition({entity_name}DTO dto);

    /**
     * 新增
     */
    {entity_name} create({entity_name}DTO dto);

    /**
     * 更新
     */
    {entity_name} update(Long id, {entity_name}DTO dto);

    /**
     * 删除
     */
    void delete(Long id);
}}
"""

    def _generate_service_impl(self, table, fields, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        
        return f"""package {package_name}.{module_name}.service.impl;

import {package_name}.{module_name}.dto.{entity_name}DTO;
import {package_name}.{module_name}.entity.{entity_name};
import {package_name}.{module_name}.mapper.{entity_name}Mapper;
import {package_name}.{module_name}.service.{entity_name}Service;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * {table.name}ServiceImpl实现类
 */
@Service
@Transactional
public class {entity_name}ServiceImpl implements {entity_name}Service {{

    private final {entity_name}Mapper {entity_name.lower()}Mapper;

    public {entity_name}ServiceImpl({entity_name}Mapper {entity_name.lower()}Mapper) {{
        this.{entity_name.lower()}Mapper = {entity_name.lower()}Mapper;
    }}

    @Override
    @Transactional(readOnly = true)
    public {entity_name} findById(Long id) {{
        return {entity_name.lower()}Mapper.selectById(id);
    }}

    @Override
    @Transactional(readOnly = true)
    public List<{entity_name}> findAll() {{
        return {entity_name.lower()}Mapper.selectAll();
    }}

    @Override
    @Transactional(readOnly = true)
    public List<{entity_name}> findByCondition({entity_name}DTO dto) {{
        {entity_name} entity = new {entity_name}();
        BeanUtils.copyProperties(dto, entity);
        return {entity_name.lower()}Mapper.selectByCondition(entity);
    }}

    @Override
    public {entity_name} create({entity_name}DTO dto) {{
        {entity_name} entity = new {entity_name}();
        BeanUtils.copyProperties(dto, entity);
        {entity_name.lower()}Mapper.insert(entity);
        return entity;
    }}

    @Override
    public {entity_name} update(Long id, {entity_name}DTO dto) {{
        {entity_name} entity = {entity_name.lower()}Mapper.selectById(id);
        if (entity == null) {{
            throw new RuntimeException("{entity_name}不存在");
        }}
        BeanUtils.copyProperties(dto, entity);
        entity.setId(id);
        {entity_name.lower()}Mapper.updateById(entity);
        return entity;
    }}

    @Override
    public void delete(Long id) {{
        {entity_name} entity = {entity_name.lower()}Mapper.selectById(id);
        if (entity == null) {{
            throw new RuntimeException("{entity_name}不存在");
        }}
        {entity_name.lower()}Mapper.deleteById(id);
    }}
}}
"""

    def _generate_controller(self, table, package_name, module_name):
        entity_name = table.name.replace('代码表', '')
        api_name = entity_name.lower()
        
        return f"""package {package_name}.{module_name}.controller;

import {package_name}.{module_name}.dto.{entity_name}DTO;
import {package_name}.{module_name}.entity.{entity_name};
import {package_name}.{module_name}.service.{entity_name}Service;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * {table.name}Controller控制器
 */
@RestController
@RequestMapping("/api/{api_name}")
public class {entity_name}Controller {{

    private final {entity_name}Service {entity_name.lower()}Service;

    public {entity_name}Controller({entity_name}Service {entity_name.lower()}Service) {{
        this.{entity_name.lower()}Service = {entity_name.lower()}Service;
    }}

    /**
     * 根据ID查询
     */
    @GetMapping("/{{id}}")
    public ResponseEntity<{entity_name}> getById(@PathVariable Long id) {{
        {entity_name} entity = {entity_name.lower()}Service.findById(id);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 查询所有
     */
    @GetMapping
    public ResponseEntity<List<{entity_name}>> getAll() {{
        List<{entity_name}> list = {entity_name.lower()}Service.findAll();
        return ResponseEntity.ok(list);
    }}

    /**
     * 根据条件查询
     */
    @PostMapping("/search")
    public ResponseEntity<List<{entity_name}>> search(@RequestBody {entity_name}DTO dto) {{
        List<{entity_name}> list = {entity_name.lower()}Service.findByCondition(dto);
        return ResponseEntity.ok(list);
    }}

    /**
     * 新增
     */
    @PostMapping
    public ResponseEntity<{entity_name}> create(@Validated @RequestBody {entity_name}DTO dto) {{
        {entity_name} entity = {entity_name.lower()}Service.create(dto);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 更新
     */
    @PutMapping("/{{id}}")
    public ResponseEntity<{entity_name}> update(@PathVariable Long id, @Validated @RequestBody {entity_name}DTO dto) {{
        {entity_name} entity = {entity_name.lower()}Service.update(id, dto);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 删除
     */
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {{
        {entity_name.lower()}Service.delete(id);
        return ResponseEntity.ok().build();
    }}
}}
"""

    def _generate_mapper_xml(self, table, fields):
        entity_name = table.name.replace('代码表', '')
        table_name = table.name.replace('代码表', '').lower()
        base_colums = ','.join([f.field_name for f in fields])
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.{table_name}.mapper.{entity_name}Mapper">

    <resultMap id="BaseResultMap" type="{entity_name}">
        <id column="id" property="id"/>
{self._generate_result_map(fields)}
    </resultMap>

    <sql id="Base_Column_List">
        id, {base_colums}
    </sql>

    <select id="selectById" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM {table_name}
        WHERE id = #{{id}}
    </select>

    <select id="selectAll" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM {table_name}
        ORDER BY id DESC
    </select>

    <select id="selectByCondition" resultMap="BaseResultMap" parameterType="{entity_name}">
        SELECT <include refid="Base_Column_List"/>
        FROM {table_name}
        <where>
{self._generate_where_conditions(fields)}
        </where>
        ORDER BY id DESC
    </select>

    <insert id="insert" parameterType="{entity_name}" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO {table_name} ({base_colums})
        VALUES ({','.join([f'#{{{f.field_name}}}' for f in fields])})
    </insert>

    <update id="updateById" parameterType="{entity_name}">
        UPDATE {table_name}
        <set>
{self._generate_set_clause(fields)}
        </set>
        WHERE id = #{{id}}
    </update>

    <delete id="deleteById">
        DELETE FROM {table_name} WHERE id = #{{id}}
    </delete>

</mapper>
"""

    def _generate_pom(self, module_name):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>{module_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>{module_name}</name>
    <description>{module_name} Spring Boot Application</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>21</java.version>
        <mybatis-spring-boot-starter.version>3.0.2</mybatis-spring-boot-starter.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>${{mybatis-spring-boot-starter.version}}</version>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
"""

    def _generate_application(self, module_name):
        return f"""package com.example.{module_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * {module_name} Spring Boot 启动类
 */
@SpringBootApplication
public class {module_name.capitalize()}Application {{

    public static void main(String[] args) {{
        SpringApplication.run({module_name.capitalize()}Application.class, args);
    }}
}}
"""

    def _generate_application_yaml(self, package_name, module_name):
        return f"""server:
  port: 8080

spring:
  application:
    name: {module_name}
  
  datasource:
    url: jdbc:mysql://localhost:3306/example_db?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: admin
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: {package_name}.{module_name}.entity

logging:
  level:
    {package_name}.{module_name}.mapper: DEBUG
"""

    def _get_java_type(self, field_type, length):
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'decimal': 'BigDecimal',
            'date': 'Date',
            'datetime': 'Date',
            'boolean': 'Boolean',
            'text': 'String',
        }
        return type_mapping.get(field_type, 'String')

    def _generate_getters_setters(self, fields):
        code = ''
        for field in fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            capitalized = field_name[0].upper() + field_name[1:]
            
            code += f"""
    public {java_type} get{capitalized}() {{ return {field_name}; }}
    public void set{capitalized}({java_type} {field_name}) {{ this.{field_name} = {field_name}; }}"""
        
        return code

    def _generate_result_map(self, fields):
        code = ''
        for field in fields:
            code += f"""        <result column="{field.field_name}" property="{field.field_name}"/>\n"""
        return code

    def _generate_where_conditions(self, fields):
        code = ''
        for field in fields:
            code += f"""            <if test="{field.field_name} != null">AND {field.field_name} = #{{{field.field_name}}}</if>\n"""
        return code

    def _generate_set_clause(self, fields):
        code = ''
        for field in fields:
            code += f"""            <if test="{field.field_name} != null">{field.field_name} = #{{{field.field_name}}},</if>\n"""
        return code


class SqlManagerView(View):
    def get(self, request):
        logger.info(f"[SqlManagerView] 加载SQL管理器页面，请求路径: {request.path}")
        context = {
            'query': '',
            'results': [],
            'columns': [],
            'error': '',
            'success': '',
        }
        return render(request, 'parameter/sql_manager.html', context)

    def post(self, request):
        query = request.POST.get('query', '').strip()
        logger.info(f"[SqlManagerView] 开始执行SQL查询，查询内容: {query[:200]}..." if len(query) > 200 else f"[SqlManagerView] 开始执行SQL查询，查询内容: {query}")
        
        if not query:
            logger.warning(f"[SqlManagerView] SQL查询语句为空")
            return render(request, 'parameter/sql_manager.html', {
                'query': '',
                'results': [],
                'columns': [],
                'error': '请输入SQL查询语句',
                'success': '',
            })
        
        from django.db import connection
        
        try:
            with connection.cursor() as cursor:
                logger.info(f"[SqlManagerView] 执行SQL语句: {query[:100]}...")
                cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
                    logger.info(f"[SqlManagerView] SELECT查询成功，返回 {len(results)} 条记录，列数: {len(columns)}")
                    
                    context = {
                        'query': query,
                        'results': results,
                        'columns': columns,
                        'error': '',
                        'success': f'查询成功，返回 {len(results)} 条记录',
                    }
                else:
                    logger.info(f"[SqlManagerView] SQL执行成功，影响 {cursor.rowcount} 行")
                    context = {
                        'query': query,
                        'results': [],
                        'columns': [],
                        'error': '',
                        'success': f'执行成功，影响 {cursor.rowcount} 行',
                    }
        except Exception as e:
            logger.error(f"[SqlManagerView] SQL执行失败: {str(e)}", exc_info=True)
            context = {
                'query': query,
                'results': [],
                'columns': [],
                'error': str(e),
                'success': '',
            }
        
        return render(request, 'parameter/sql_manager.html', context)