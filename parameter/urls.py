from django.urls import path
from . import views
from .ai import views as ai_views

urlpatterns = [
    path('', views.index, name='index'),
    path('tables/', views.ParameterTableListView.as_view(), name='table_list'),
    path('tables/<str:table_id>/', views.ParameterTableDetailView.as_view(), name='table_detail'),
    path('metadata/', views.MetadataListView.as_view(), name='metadata_list'),
    path('requirements/', views.RequirementListView.as_view(), name='requirement_list'),
    path('requirements/<str:req_id>/', views.RequirementDetailView.as_view(), name='requirement_detail'),
    path('requirements/create/', views.RequirementCreateView.as_view(), name='requirement_create'),
    path('task-documents/', views.TaskDocumentListView.as_view(), name='task_document_list'),
    path('task-documents/export/<str:doc_id>/', views.TaskDocumentExportView.as_view(), name='task_document_export'),
    path('config-scripts/', views.ConfigScriptListView.as_view(), name='config_script_list'),
    path('index-id/', views.IndexIdConfigListView.as_view(), name='index_id_config_list'),
    path('test-cases/', views.TestCaseListView.as_view(), name='test_case_list'),
    path('automation-test/', views.AutomationTestResultView.as_view(), name='automation_test_result'),
    path('sql-manager/', views.SqlManagerView.as_view(), name='sql_manager'),
    path('ai-analysis/', ai_views.AIAnalysisView.as_view(), name='ai_analysis'),
    path('ai-analysis/unification/', ai_views.AIUnificationAnalysisView.as_view(), name='ai_unification_analysis'),
    path('ai-analysis/normalization/', ai_views.AINormalizationAnalysisView.as_view(), name='ai_normalization_analysis'),
    path('ai-generation/', ai_views.AIGenerationView.as_view(), name='ai_generation'),
    path('ai-generation/task-document/', ai_views.AITaskDocumentGenerationView.as_view(), name='ai_task_document_generation'),
    path('ai-generation/test-case/', ai_views.AITestCaseGenerationView.as_view(), name='ai_test_case_generation'),
    path('ai-generation/sql/', ai_views.AISQLGenerationView.as_view(), name='ai_sql_generation'),
]