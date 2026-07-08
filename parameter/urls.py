"""
URL路由配置
定义parameter应用的所有URL路由，包括认证、参数表、元数据、需求、AI等模块
"""
from django.urls import path
from . import auth_views
from .ai import views as ai_views

from .views.home import index
from .views.parameter_table import ParameterTableListView, ParameterTableDetailView, ParameterTableCreateView, ParameterTableEditView, ParameterTableDeleteView, ParameterTableFieldConfigurationView, FieldAddView, FieldEditView, FieldDeleteView
from .views.metadata import MetadataListView, MetadataCreateView, MetadataEditView, MetadataDeleteView
from .views.requirement import RequirementListView, RequirementDetailView, RequirementCreateView, RequirementEditView, RequirementDeleteView, RequirementSubmitView, RequirementProcessView, RequirementCompleteView, RequirementUpdateStatusView, RequirementExportView, RequirementImportView, RequirementImportEditView, RequirementExportResponseView, RequirementImportResponseView, RequirementFieldConfigView, RequirementFieldAddView, RequirementFieldEditView, RequirementFieldDeleteView, RequirementFieldConfirmView
from .views.task_document import TaskDocumentListView, TaskDocumentExportView, TaskDocumentCreateView, TaskDocumentEditView, TaskDocumentDeleteView
from .views.config import IndexIdConfigListView, IndexIdConfigCreateView, IndexIdConfigEditView, IndexIdConfigDeleteView
from .views.test import TestCaseListView, AutomationTestResultView
from .views.springboot import SpringBootGeneratorView, SpringBootDownloadView
from .views.sql_manager import SqlManagerView

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password/', auth_views.ChangePasswordView.as_view(), name='change_password'),
    path('users/', auth_views.UserListView.as_view(), name='user_list'),
    path('users/create/', auth_views.UserCreateView.as_view(), name='user_create'),
    path('users/edit/<str:user_id>/', auth_views.UserEditView.as_view(), name='user_edit'),
    path('users/delete/<str:user_id>/', auth_views.UserDeleteView.as_view(), name='user_delete'),
    path('', index, name='index'),
    path('tables/', ParameterTableListView.as_view(), name='table_list'),
    path('tables/create/', ParameterTableCreateView.as_view(), name='table_create'),
    path('tables/edit/<str:table_id>/', ParameterTableEditView.as_view(), name='table_edit'),
    path('tables/delete/<str:table_id>/', ParameterTableDeleteView.as_view(), name='table_delete'),
    path('tables/<str:table_id>/fields/', ParameterTableFieldConfigurationView.as_view(), name='table_fields'),
    path('tables/<str:table_id>/fields/add/', FieldAddView.as_view(), name='field_add'),
    path('tables/<str:table_id>/fields/edit/<str:field_id>/', FieldEditView.as_view(), name='field_edit'),
    path('tables/<str:table_id>/fields/delete/<str:field_id>/', FieldDeleteView.as_view(), name='field_delete'),
    path('tables/<str:table_id>/', ParameterTableDetailView.as_view(), name='table_detail'),
    path('metadata/', MetadataListView.as_view(), name='metadata_list'),
    path('metadata/create/', MetadataCreateView.as_view(), name='metadata_create'),
    path('metadata/edit/<str:metadata_id>/', MetadataEditView.as_view(), name='metadata_edit'),
    path('metadata/delete/<str:metadata_id>/', MetadataDeleteView.as_view(), name='metadata_delete'),
    path('requirements/', RequirementListView.as_view(), name='requirement_list'),
    path('requirements/create/', RequirementCreateView.as_view(), name='requirement_create'),
    path('requirements/edit/<str:req_id>/', RequirementEditView.as_view(), name='requirement_edit'),
    path('requirements/delete/<str:req_id>/', RequirementDeleteView.as_view(), name='requirement_delete'),
    path('requirements/submit/<str:req_id>/', RequirementSubmitView.as_view(), name='requirement_submit'),
    path('requirements/process/<str:req_id>/', RequirementProcessView.as_view(), name='requirement_process'),
    path('requirements/complete/<str:req_id>/', RequirementCompleteView.as_view(), name='requirement_complete'),
    path('requirements/export/', RequirementExportView.as_view(), name='requirement_export'),
    path('requirements/import/', RequirementImportView.as_view(), name='requirement_import'),
    path('requirements/import/edit/', RequirementImportEditView.as_view(), name='requirement_import_edit'),
    path('requirements/export-response/<str:import_key>/', RequirementExportResponseView.as_view(), name='requirement_export_response'),
    path('requirements/import-response/', RequirementImportResponseView.as_view(), name='requirement_import_response'),
    path('requirements/<str:req_id>/fields/', RequirementFieldConfigView.as_view(), name='requirement_field_config'),
    path('requirements/<str:req_id>/fields/add/', RequirementFieldAddView.as_view(), name='requirement_field_add'),
    path('requirements/<str:req_id>/fields/edit/<str:field_id>/', RequirementFieldEditView.as_view(), name='requirement_field_edit'),
    path('requirements/<str:req_id>/fields/delete/<str:field_id>/', RequirementFieldDeleteView.as_view(), name='requirement_field_delete'),
    path('requirements/<str:req_id>/fields/confirm/', RequirementFieldConfirmView.as_view(), name='requirement_field_confirm'),
    path('requirements/<str:req_id>/', RequirementDetailView.as_view(), name='requirement_detail'),
    path('requirements/<str:req_id>/update-status/', RequirementUpdateStatusView.as_view(), name='requirement_update_status'),
    path('task-documents/', TaskDocumentListView.as_view(), name='task_document_list'),
    path('task-documents/create/', TaskDocumentCreateView.as_view(), name='task_document_create'),
    path('task-documents/edit/<str:doc_id>/', TaskDocumentEditView.as_view(), name='task_document_edit'),
    path('task-documents/delete/<str:doc_id>/', TaskDocumentDeleteView.as_view(), name='task_document_delete'),
    path('task-documents/export/<str:doc_id>/', TaskDocumentExportView.as_view(), name='task_document_export'),
    path('index-id/', IndexIdConfigListView.as_view(), name='index_id_config_list'),
    path('index-id/create/', IndexIdConfigCreateView.as_view(), name='index_id_config_create'),
    path('index-id/edit/<str:config_id>/', IndexIdConfigEditView.as_view(), name='index_id_config_edit'),
    path('index-id/delete/<str:config_id>/', IndexIdConfigDeleteView.as_view(), name='index_id_config_delete'),
    path('test-cases/', TestCaseListView.as_view(), name='test_case_list'),
    path('automation-test/', AutomationTestResultView.as_view(), name='automation_test_result'),
    path('generator/', SpringBootGeneratorView.as_view(), name='code_generator'),
    path('generator/download/', SpringBootDownloadView.as_view(), name='code_download'),
    path('sql-manager/', SqlManagerView.as_view(), name='sql_manager'),
    path('ai-analysis/', ai_views.AIAnalysisView.as_view(), name='ai_analysis'),
    path('ai-analysis/unification/', ai_views.AIUnificationAnalysisView.as_view(), name='ai_unification_analysis'),
    path('ai-analysis/normalization/', ai_views.AINormalizationAnalysisView.as_view(), name='ai_normalization_analysis'),
    path('ai-generation/', ai_views.AIGenerationView.as_view(), name='ai_generation'),
    path('ai-generation/task-document/', ai_views.AITaskDocumentGenerationView.as_view(), name='ai_task_document_generation'),
    path('ai-generation/test-case/', ai_views.AITestCaseGenerationView.as_view(), name='ai_test_case_generation'),
    path('ai-generation/sql/', ai_views.AISQLGenerationView.as_view(), name='ai_sql_generation'),
]
