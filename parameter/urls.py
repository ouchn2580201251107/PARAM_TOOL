"""
URL路由配置
定义parameter应用的所有URL路由，包括认证、参数表、元数据、需求、AI等模块
"""
from django.urls import path
from . import views
from . import auth_views
from .ai import views as ai_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password/', auth_views.ChangePasswordView.as_view(), name='change_password'),
    path('users/', auth_views.UserListView.as_view(), name='user_list'),
    path('users/create/', auth_views.UserCreateView.as_view(), name='user_create'),
    path('users/edit/<str:user_id>/', auth_views.UserEditView.as_view(), name='user_edit'),
    path('users/delete/<str:user_id>/', auth_views.UserDeleteView.as_view(), name='user_delete'),
    path('', views.index, name='index'),
    path('tables/', views.ParameterTableListView.as_view(), name='table_list'),
    path('tables/<str:table_id>/', views.ParameterTableDetailView.as_view(), name='table_detail'),
    path('metadata/', views.MetadataListView.as_view(), name='metadata_list'),
    path('metadata/create/', views.MetadataCreateView.as_view(), name='metadata_create'),
    path('metadata/edit/<str:metadata_id>/', views.MetadataEditView.as_view(), name='metadata_edit'),
    path('metadata/delete/<str:metadata_id>/', views.MetadataDeleteView.as_view(), name='metadata_delete'),
    path('requirements/', views.RequirementListView.as_view(), name='requirement_list'),
    path('requirements/create/', views.RequirementCreateView.as_view(), name='requirement_create'),
    path('requirements/<str:req_id>/', views.RequirementDetailView.as_view(), name='requirement_detail'),
    path('task-documents/', views.TaskDocumentListView.as_view(), name='task_document_list'),
    path('task-documents/export/<str:doc_id>/', views.TaskDocumentExportView.as_view(), name='task_document_export'),
    path('config-scripts/', views.ConfigScriptListView.as_view(), name='config_script_list'),
    path('index-id/', views.IndexIdConfigListView.as_view(), name='index_id_config_list'),
    path('test-cases/', views.TestCaseListView.as_view(), name='test_case_list'),
    path('automation-test/', views.AutomationTestResultView.as_view(), name='automation_test_result'),
    path('springboot-generator/', views.SpringBootGeneratorView.as_view(), name='springboot_generator'),
    path('springboot-download/', views.SpringBootDownloadView.as_view(), name='springboot_download'),
    path('sql-manager/', views.SqlManagerView.as_view(), name='sql_manager'),
    path('ai-analysis/', ai_views.AIAnalysisView.as_view(), name='ai_analysis'),
    path('ai-analysis/unification/', ai_views.AIUnificationAnalysisView.as_view(), name='ai_unification_analysis'),
    path('ai-analysis/normalization/', ai_views.AINormalizationAnalysisView.as_view(), name='ai_normalization_analysis'),
    path('ai-generation/', ai_views.AIGenerationView.as_view(), name='ai_generation'),
    path('ai-generation/task-document/', ai_views.AITaskDocumentGenerationView.as_view(), name='ai_task_document_generation'),
    path('ai-generation/test-case/', ai_views.AITestCaseGenerationView.as_view(), name='ai_test_case_generation'),
    path('ai-generation/sql/', ai_views.AISQLGenerationView.as_view(), name='ai_sql_generation'),
]