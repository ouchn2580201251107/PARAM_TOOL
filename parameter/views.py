import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Count

from .models import ParameterTable, Metadata, FieldDefinition, Requirement, TaskDocument, ConfigScript, IndexIdConfig, TestCase, AutomationTestResult

logger = logging.getLogger(__name__)

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

class MetadataListView(View):
    def get(self, request):
        logger.info(f"[MetadataListView] 开始查询元数据列表，请求路径: {request.path}")
        try:
            metadata_list = Metadata.objects.all()
            logger.info(f"[MetadataListView] 元数据查询完成，记录数: {metadata_list.count()}")
            
            field_types = Metadata.objects.values_list('field_type', flat=True).distinct()
            logger.info(f"[MetadataListView] 获取到 {len(list(field_types))} 个不同的字段类型")
            
            context = {
                'metadata_list': metadata_list,
                'field_types': field_types,
            }
            logger.info(f"[MetadataListView] 元数据列表查询成功，即将渲染模板")
            return render(request, 'parameter/metadata_list.html', context)
        except Exception as e:
            logger.error(f"[MetadataListView] 元数据列表查询失败: {str(e)}", exc_info=True)
            raise

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

class RequirementCreateView(View):
    def get(self, request):
        logger.info(f"[RequirementCreateView] 开始加载需求创建页面，请求路径: {request.path}")
        try:
            tables = ParameterTable.objects.all()
            logger.info(f"[RequirementCreateView] 参数表查询完成，记录数: {tables.count()}")
            
            context = {
                'tables': tables,
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