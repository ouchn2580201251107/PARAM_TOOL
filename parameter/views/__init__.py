"""
视图模块统一导出入口
从各子模块导入所有视图类和函数，方便其他模块引用
"""

from .home import index
from .parameter_table import ParameterTableListView, ParameterTableDetailView
from .metadata import MetadataListView, MetadataCreateView, MetadataEditView, MetadataDeleteView
from .requirement import RequirementListView, RequirementDetailView, RequirementCreateView, RequirementUpdateStatusView
from .task_document import TaskDocumentListView, TaskDocumentExportView
from .config import ConfigScriptListView, ConfigScriptSubmitView, ProductTableConfigListView
from .test import TestCaseListView, AutomationTestResultView
from .springboot import SpringBootGeneratorView, SpringBootDownloadView
from .sql_manager import SqlManagerView

__all__ = [
    'index',
    'ParameterTableListView',
    'ParameterTableDetailView',
    'MetadataListView',
    'MetadataCreateView',
    'MetadataEditView',
    'MetadataDeleteView',
    'RequirementListView',
    'RequirementDetailView',
    'RequirementCreateView',
    'RequirementUpdateStatusView',
    'TaskDocumentListView',
    'TaskDocumentExportView',
    'ConfigScriptListView',
    'ConfigScriptSubmitView',
    'ProductTableConfigListView',
    'TestCaseListView',
    'AutomationTestResultView',
    'SpringBootGeneratorView',
    'SpringBootDownloadView',
    'SqlManagerView',
]
