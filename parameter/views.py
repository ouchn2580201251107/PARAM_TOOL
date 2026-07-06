"""
主业务视图模块
实现参数表管理、元数据管理、需求管理、任务书管理、配置脚本管理、测试管理、Spring Boot代码生成等核心业务功能
"""
import logging
import zipfile
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Count
from django.utils.decorators import method_decorator

from .auth_views import login_required, admin_required, role_required
from .models import ParameterTable, Metadata, FieldDefinition, Requirement, TaskDocument, ConfigScript, IndexIdConfig, TestCase, AutomationTestResult
from .utils.springboot_generator import SpringBootCodeGenerator

logger = logging.getLogger(__name__)

@login_required
def index(request):
    """
    首页视图
    展示系统概览数据，包括参数表、需求、任务书、配置脚本的统计信息
    """
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
    """
    参数表列表视图
    展示所有参数表的业务说明底账，支持按业务领域、状态和名称搜索过滤
    """
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
    """
    参数表详情视图
    展示参数表的详细信息，包括字段定义列表
    """
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
    """
    元数据创建视图
    仅管理员和技术人员可访问，用于创建新的元数据配置
    """
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
    """
    Spring Boot代码生成器视图
    仅管理员可访问，根据参数表元数据生成完整的Spring Boot项目代码预览
    生成内容包括：Entity、DTO、Mapper、Service、ServiceImpl、Controller、Mapper XML等
    """
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
            
            generator = SpringBootCodeGenerator(table, fields, package_name, module_name)
            code = generator.generate_all()
            
            context = {
                'table': table,
                'fields': fields,
                'package_name': package_name,
                'module_name': module_name,
                'entity_code': code['entity'],
                'dto_code': code['dto'],
                'mapper_code': code['mapper'],
                'service_code': code['service'],
                'controller_code': code['controller'],
                'mapper_xml_code': code['mapper_xml'],
            }
            
            return render(request, 'parameter/springboot_generator.html', context)
        except ParameterTable.DoesNotExist:
            return render(request, 'parameter/springboot_generator.html', {
                'tables': ParameterTable.objects.all(),
                'error': '参数表不存在',
            })


@method_decorator(admin_required, name='dispatch')
class SpringBootDownloadView(View):
    """
    Spring Boot代码下载视图
    仅管理员可访问，将生成的Spring Boot项目代码打包为ZIP文件供下载
    包含完整的项目结构：pom.xml、Application、各层代码、配置文件等
    """
    def post(self, request):
        table_id = request.POST.get('table_id')
        package_name = request.POST.get('package_name', 'com.example')
        module_name = request.POST.get('module_name', 'demo')
        
        try:
            table = ParameterTable.objects.get(id=table_id)
            fields = FieldDefinition.objects.filter(parameter_table=table).order_by('sort_order')
            
            generator = SpringBootCodeGenerator(table, fields, package_name, module_name)
            code = generator.generate_all()
            
            entity_name = table.name.replace('代码表', '')
            base_path = f'{module_name}/src/main/java/{generator.package_path}/{module_name}'
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(f'{base_path}/entity/{entity_name}.java', code['entity'])
                zf.writestr(f'{base_path}/dto/{entity_name}DTO.java', code['dto'])
                zf.writestr(f'{base_path}/mapper/{entity_name}Mapper.java', code['mapper'])
                zf.writestr(f'{base_path}/service/{entity_name}Service.java', code['service'])
                zf.writestr(f'{base_path}/service/impl/{entity_name}ServiceImpl.java', code['service_impl'])
                zf.writestr(f'{base_path}/controller/{entity_name}Controller.java', code['controller'])
                zf.writestr(f'{module_name}/src/main/resources/mapper/{entity_name}Mapper.xml', code['mapper_xml'])
                zf.writestr(f'{module_name}/pom.xml', code['pom'])
                zf.writestr(f'{base_path}/{module_name.capitalize()}Application.java', code['application'])
                zf.writestr(f'{module_name}/src/main/resources/application.yml', code['application_yaml'])
            
            zip_buffer.seek(0)
            
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{module_name}-springboot.zip"'
            
            return response
        except ParameterTable.DoesNotExist:
            return HttpResponse('参数表不存在', status=400)


@method_decorator(admin_required, name='dispatch')
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