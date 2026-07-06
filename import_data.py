"""
数据导入脚本
从CSV文件导入系统初始数据，包括参数表、元数据、字段定义、需求、任务书等

使用方法：
    python import_data.py
"""
import os
import csv
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'param_tool.settings')

import django
django.setup()

from parameter.models import ParameterTable, Metadata, FieldDefinition, Requirement, TaskDocument, ConfigScript, IndexIdConfig, TestCase, AutomationTestResult

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parameter', 'data')
"""CSV数据文件存放目录"""

def read_csv_file(filename):
    """
    读取CSV文件并返回字典列表
    
    Args:
        filename: CSV文件名
        
    Returns:
        list: 包含每行数据的字典列表
    """
    file_path = os.path.join(DATA_DIR, filename)
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data

def import_parameter_tables():
    print("导入参数表数据...")
    ParameterTable.objects.all().delete()
    data = read_csv_file('parameter_tables.csv')
    for row in data:
        ParameterTable.objects.create(
            id=int(row['id']),
            name=row['name'],
            business_description=row['business_description'],
            domain=row['domain'],
            owner=row['owner'],
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            version=int(row['version'])
        )
    print(f"  导入 {len(data)} 条记录")

def import_metadata():
    print("导入元数据...")
    Metadata.objects.all().delete()
    data = read_csv_file('metadata.csv')
    for row in data:
        Metadata.objects.create(
            id=int(row['id']),
            name=row['name'],
            field_type=row['field_type'],
            length=int(row['length']) if row['length'] else None,
            decimal_places=int(row['decimal_places']) if row['decimal_places'] else None,
            control_type=row['control_type'],
            default_value=row['default_value'] if row['default_value'] else None,
            is_required=row['is_required'] == 'True',
            validation_rule=row['validation_rule'] if row['validation_rule'] else None,
            description=row['description'] if row['description'] else None
        )
    print(f"  导入 {len(data)} 条记录")

def import_field_definitions():
    print("导入字段定义...")
    FieldDefinition.objects.all().delete()
    data = read_csv_file('field_definitions.csv')
    success_count = 0
    for row in data:
        try:
            metadata = Metadata.objects.get(id=int(row['metadata_id'])) if row['metadata_id'] else None
        except Metadata.DoesNotExist:
            metadata = None
        
        try:
            length_val = int(row['length']) if row['length'] and row['length'].isdigit() else None
            decimal_val = int(row['decimal_places']) if row['decimal_places'] and row['decimal_places'].isdigit() else None
            sort_val = int(row['sort_order']) if row['sort_order'] and row['sort_order'].isdigit() else 0
            
            FieldDefinition.objects.create(
                id=int(row['id']),
                parameter_table_id=int(row['parameter_table_id']),
                metadata=metadata,
                field_name=row['field_name'],
                display_name=row['display_name'],
                field_type=row['field_type'],
                length=length_val,
                decimal_places=decimal_val,
                control_type=row['control_type'],
                storage_type=row['storage_type'],
                is_visible=row['is_visible'] == 'True',
                is_required=row['is_required'] == 'True',
                validation_rule=row.get('validation_rule') or None,
                sort_order=sort_val,
                is_custom=row['is_custom'] == 'True',
                custom_requirement=row.get('custom_requirement') or None
            )
            success_count += 1
        except Exception as e:
            print(f"  跳过字段定义 {row.get('id', 'unknown')}: {e}")
    print(f"  导入 {success_count}/{len(data)} 条记录")

def import_requirements():
    print("导入需求数据...")
    Requirement.objects.all().delete()
    data = read_csv_file('requirements.csv')
    for row in data:
        try:
            table = ParameterTable.objects.get(id=int(row['parameter_table_id'])) if row['parameter_table_id'] else None
        except ParameterTable.DoesNotExist:
            table = None
        
        Requirement.objects.create(
            id=int(row['id']),
            requirement_no=row['requirement_no'],
            title=row['title'],
            requirement_type=row['requirement_type'],
            parameter_table=table,
            business_description=row['business_description'],
            requester=row['requester'],
            request_date=row['request_date'],
            status=row['status'],
            story_points=int(row['story_points']) if row['story_points'] else None,
            sprint=row['sprint'] if row['sprint'] else None,
            project_platform_id=row['project_platform_id'] if row['project_platform_id'] else None
        )
    print(f"  导入 {len(data)} 条记录")

def import_task_documents():
    print("导入任务书数据...")
    TaskDocument.objects.all().delete()
    data = read_csv_file('task_documents.csv')
    for row in data:
        try:
            TaskDocument.objects.create(
                id=int(row['id']),
                requirement_id=int(row['requirement_id']),
                document_no=row['document_no'],
                title=row['title'],
                document_type=row['document_type'],
                content=row['content'],
                generated_at=row['generated_at'],
                exported_at=row['exported_at'] if row['exported_at'] else None
            )
        except Exception as e:
            print(f"  跳过任务书 {row['id']}: {e}")
    print(f"  导入 {len(data)} 条记录")

def import_config_scripts():
    print("导入配置脚本...")
    ConfigScript.objects.all().delete()
    data = read_csv_file('config_scripts.csv')
    success_count = 0
    for row in data:
        try:
            ConfigScript.objects.create(
                id=int(row['id']),
                requirement_id=int(row['requirement_id']),
                script_type=row['script_type'],
                script_content=row['script_content'],
                status=row['status'],
                submitted_at=None,
                deployed_at=None,
                environment=row['environment'] if row['environment'] else None
            )
            success_count += 1
        except Exception as e:
            print(f"  跳过配置脚本 {row.get('id', 'unknown')}: {e}")
    print(f"  导入 {success_count}/{len(data)} 条记录")

def import_index_id_configs():
    print("导入INDEXID配置...")
    IndexIdConfig.objects.all().delete()
    data = read_csv_file('index_id_configs.csv')
    for row in data:
        try:
            IndexIdConfig.objects.create(
                id=int(row['id']),
                parameter_table_id=int(row['parameter_table_id']),
                index_id=row['index_id'],
                business_name=row['business_name'],
                business_description=row['business_description'] if row['business_description'] else None,
                custom_column_names=json.loads(row['custom_column_names']) if row['custom_column_names'] else {},
                display_fields=json.loads(row['display_fields']) if row['display_fields'] else [],
                validation_rules=json.loads(row['validation_rules']) if row['validation_rules'] else {},
                created_at=row['created_at']
            )
        except Exception as e:
            print(f"  跳过INDEXID配置 {row['id']}: {e}")
    print(f"  导入 {len(data)} 条记录")

def import_test_cases():
    print("导入测试用例...")
    TestCase.objects.all().delete()
    data = read_csv_file('test_cases.csv')
    for row in data:
        try:
            TestCase.objects.create(
                id=int(row['id']),
                requirement_id=int(row['requirement_id']),
                case_no=row['case_no'],
                title=row['title'],
                case_type=row['case_type'],
                preconditions=row['preconditions'] if row['preconditions'] else None,
                steps=row['steps'],
                expected_result=row['expected_result'],
                status=row['status'],
                automated=row['automated'] == 'True',
                created_at=row['created_at']
            )
        except Exception as e:
            print(f"  跳过测试用例 {row['id']}: {e}")
    print(f"  导入 {len(data)} 条记录")

def import_automation_test_results():
    print("导入自动化测试结果...")
    AutomationTestResult.objects.all().delete()
    data = read_csv_file('automation_test_results.csv')
    for row in data:
        try:
            AutomationTestResult.objects.create(
                id=int(row['id']),
                test_case_id=int(row['test_case_id']),
                execution_date=row['execution_date'],
                status=row['status'],
                error_message=row['error_message'] if row['error_message'] else None,
                duration=float(row['duration']) if row['duration'] else None
            )
        except Exception as e:
            print(f"  跳过测试结果 {row['id']}: {e}")
    print(f"  导入 {len(data)} 条记录")

if __name__ == '__main__':
    print("开始导入数据...")
    print("=" * 50)
    
    import_parameter_tables()
    import_metadata()
    import_field_definitions()
    import_requirements()
    import_task_documents()
    import_config_scripts()
    import_index_id_configs()
    import_test_cases()
    import_automation_test_results()
    
    print("=" * 50)
    print("数据导入完成！")