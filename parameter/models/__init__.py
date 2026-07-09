"""
模型模块统一导出入口
从各子模块导入所有模型类，方便其他模块引用
"""

from .core import ParameterTable, Metadata, FieldDefinition
from .requirement import Requirement, TaskDocument, ConfigScript, RequirementFieldConfig
from .test import TestCase, AutomationTestResult, TestBatch
from .config import ProductTableConfig
from .auth import Role, User

__all__ = [
    'ParameterTable',
    'Metadata',
    'FieldDefinition',
    'Requirement',
    'TaskDocument',
    'ConfigScript',
    'RequirementFieldConfig',
    'TestCase',
    'AutomationTestResult',
    'TestBatch',
    'ProductTableConfig',
    'Role',
    'User',
]
