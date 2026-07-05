import logging

from .ai_client import ai_client
from parameter.models import ParameterTable, FieldDefinition, Requirement

logger = logging.getLogger(__name__)

class AIParameterTableAnalyzer:
    @staticmethod
    def analyze_unification(table_id):
        logger.info(f"[AIParameterTableAnalyzer] 开始分析参数表统一可行性，table_id: {table_id}")
        
        try:
            table = ParameterTable.objects.filter(id=table_id).first()
            if not table:
                return {"success": False, "error": "参数表不存在"}
            
            fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            
            table_info = {
                "table_name": table.name,
                "business_description": table.business_description,
                "domain": table.domain,
                "owner": table.owner,
                "status": table.status,
                "fields": [
                    {
                        "field_name": f.field_name,
                        "display_name": f.display_name,
                        "field_type": f.field_type,
                        "length": f.length,
                        "control_type": f.control_type,
                        "storage_type": f.storage_type,
                        "is_required": f.is_required,
                        "validation_rule": f.validation_rule
                    }
                    for f in fields
                ]
            }
            
            prompt = f"""分析参数表 '{table.name}' 是否可以统一到SIMPLELIST表。
业务描述：{table.business_description}
字段数量：{len(table_info['fields'])}
请根据字段结构和业务特征给出统一可行性评估。"""
            
            result = ai_client.analyze(prompt, table_info=table_info)
            logger.info(f"[AIParameterTableAnalyzer] 参数表统一分析完成，评分: {result.get('confidence', 0)}")
            
            return result
        except Exception as e:
            logger.error(f"[AIParameterTableAnalyzer] 参数表统一分析失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def analyze_normalization(table_id):
        logger.info(f"[AIParameterTableAnalyzer] 开始分析字段定义规范性，table_id: {table_id}")
        
        try:
            fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            
            fields_data = [
                {
                    "field_name": f.field_name,
                    "display_name": f.display_name,
                    "field_type": f.field_type,
                    "length": f.length,
                    "decimal_places": f.decimal_places,
                    "control_type": f.control_type,
                    "storage_type": f.storage_type,
                    "is_required": f.is_required,
                    "is_visible": f.is_visible,
                    "validation_rule": f.validation_rule,
                    "sort_order": f.sort_order,
                    "is_custom": f.is_custom
                }
                for f in fields
            ]
            
            prompt = f"""检查以下字段定义是否符合规范。
共 {len(fields_data)} 个字段，请检查：
1. 字段命名规范（大写字母+下划线）
2. 字段类型与控件类型匹配
3. 长度设置合理性
4. 必填字段标记"""
            
            result = ai_client.analyze(prompt, fields=fields_data)
            logger.info(f"[AIParameterTableAnalyzer] 字段规范性分析完成，问题数: {result.get('details', {}).get('issues_count', 0)}")
            
            return result
        except Exception as e:
            logger.error(f"[AIParameterTableAnalyzer] 字段规范性分析失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

class AIGeneratorService:
    @staticmethod
    def generate_task_document(requirement_id):
        logger.info(f"[AIGeneratorService] 开始生成任务书，requirement_id: {requirement_id}")
        
        try:
            requirement = Requirement.objects.filter(id=requirement_id).select_related('parameter_table').first()
            if not requirement:
                return {"success": False, "error": "需求不存在"}
            
            table_id = requirement.parameter_table_id if requirement.parameter_table else None
            fields = []
            if table_id:
                fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            
            requirement_data = {
                "title": requirement.title,
                "requirement_no": requirement.requirement_no,
                "requirement_type": requirement.requirement_type,
                "business_description": requirement.business_description,
                "requester": requirement.requester,
                "domain": requirement.parameter_table.domain if requirement.parameter_table else "",
                "status": requirement.status,
                "story_points": requirement.story_points,
                "sprint": requirement.sprint
            }
            
            fields_data = [
                {
                    "field_name": f.field_name,
                    "display_name": f.display_name,
                    "field_type": f.field_type,
                    "length": f.length,
                    "control_type": f.control_type,
                    "storage_type": f.storage_type,
                    "is_required": f.is_required,
                    "validation_rule": f.validation_rule
                }
                for f in fields
            ]
            
            prompt = f"""根据以下需求信息生成规范的任务书文档：
需求标题：{requirement.title}
需求编号：{requirement.requirement_no}
需求类型：{requirement.requirement_type}
业务描述：{requirement.business_description}
字段数量：{len(fields_data)}

请按标准化模板生成任务书，包含需求概述、字段定义表格、校验规则、技术要求等章节。"""
            
            result = ai_client.generate(prompt, requirement=requirement_data, fields=fields_data)
            logger.info(f"[AIGeneratorService] 任务书生成完成，字数: {result.get('details', {}).get('word_count', 0)}")
            
            return result
        except Exception as e:
            logger.error(f"[AIGeneratorService] 任务书生成失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def generate_test_cases(requirement_id):
        logger.info(f"[AIGeneratorService] 开始生成测试用例，requirement_id: {requirement_id}")
        
        try:
            requirement = Requirement.objects.filter(id=requirement_id).select_related('parameter_table').first()
            if not requirement:
                return {"success": False, "error": "需求不存在"}
            
            table_id = requirement.parameter_table_id if requirement.parameter_table else None
            fields = []
            if table_id:
                fields = FieldDefinition.objects.filter(parameter_table_id=table_id).order_by('sort_order')
            
            requirement_data = {
                "title": requirement.title,
                "requirement_no": requirement.requirement_no,
                "business_description": requirement.business_description
            }
            
            fields_data = [
                {
                    "field_name": f.field_name,
                    "field_type": f.field_type,
                    "is_required": f.is_required,
                    "validation_rule": f.validation_rule,
                    "length": f.length
                }
                for f in fields
            ]
            
            prompt = f"""根据以下需求生成测试用例：
需求标题：{requirement.title}
需求编号：{requirement.requirement_no}
字段数量：{len(fields_data)}

请生成覆盖正常流程、边界条件、异常场景的测试用例。"""
            
            result = ai_client.generate(prompt, requirement=requirement_data, fields=fields_data)
            logger.info(f"[AIGeneratorService] 测试用例生成完成，数量: {result.get('details', {}).get('total_cases', 0)}")
            
            return result
        except Exception as e:
            logger.error(f"[AIGeneratorService] 测试用例生成失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    @staticmethod
    def generate_sql(table_id, natural_query):
        logger.info(f"[AIGeneratorService] 开始生成SQL，table_id: {table_id}, query: {natural_query[:50]}")
        
        try:
            table = ParameterTable.objects.filter(id=table_id).first()
            if not table:
                return {"success": False, "error": "参数表不存在"}
            
            table_info = {
                "table_name": f"parameter_{table.name.lower()}",
                "business_description": table.business_description,
                "domain": table.domain
            }
            
            prompt = f"""根据自然语言描述生成SQL语句：
表名：{table_info['table_name']}
业务描述：{table_info['business_description']}
查询描述：{natural_query}

请生成正确的SQL语句。"""
            
            result = ai_client.generate(prompt, table_info=table_info)
            logger.info(f"[AIGeneratorService] SQL生成完成")
            
            return result
        except Exception as e:
            logger.error(f"[AIGeneratorService] SQL生成失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}