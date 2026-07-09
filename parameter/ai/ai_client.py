"""
AI客户端模块
提供AI服务的客户端封装，包含基础抽象类和Mock实现用于开发测试
"""
import logging
import json
import time

logger = logging.getLogger(__name__)

class BaseAIClient:
    """
    AI客户端基类
    定义AI服务的标准接口，具体实现需继承此类并实现analyze和generate方法
    """
    
    def analyze(self, prompt, **kwargs):
        """
        执行AI分析
        
        Args:
            prompt: 分析提示词
            **kwargs: 额外参数
            
        Returns:
            dict: 分析结果
        """
        raise NotImplementedError
    
    def generate(self, prompt, **kwargs):
        """
        执行AI生成
        
        Args:
            prompt: 生成提示词
            **kwargs: 额外参数
            
        Returns:
            dict: 生成结果
        """
        raise NotImplementedError

class MockAIClient(BaseAIClient):
    """
    Mock AI客户端
    用于开发和测试环境，模拟AI服务的返回结果，无需实际调用AI接口
    """
    
    def analyze(self, prompt, **kwargs):
        """
        模拟AI分析
        
        根据提示词内容智能返回预设的分析结果
        """
        logger.info(f"[MockAIClient] 执行AI分析: {prompt[:100]}...")
        time.sleep(1)
        
        if "参数表统一" in prompt or "SIMPLELIST" in prompt:
            return self._mock_unification_analysis(prompt, kwargs)
        
        if "字段" in prompt and "规范" in prompt or "规范性" in prompt:
            return self._mock_normalization_analysis(prompt, kwargs)
        
        return {
            "success": True,
            "confidence": 0.85,
            "result": "分析完成。建议：请根据业务需求进行评估。",
            "details": {}
        }
    
    def generate(self, prompt, **kwargs):
        """
        模拟AI生成
        
        根据提示词内容智能返回预设的生成结果
        """
        logger.info(f"[MockAIClient] 执行AI生成: {prompt[:100]}...")
        time.sleep(1.5)
        
        if "任务书" in prompt:
            return self._mock_task_document_generation(prompt, kwargs)
        
        if "测试用例" in prompt:
            return self._mock_test_case_generation(prompt, kwargs)
        
        if "SQL" in prompt:
            return self._mock_sql_generation(prompt, kwargs)
        
        return {
            "success": True,
            "confidence": 0.82,
            "result": "生成完成。",
            "details": []
        }
    
    def _mock_unification_analysis(self, prompt, kwargs):
        table_info = kwargs.get('table_info', {})
        fields = table_info.get('fields', [])
        
        score = 0.6
        suggestions = []
        reasons = []
        
        if len(fields) <= 8:
            score += 0.2
            reasons.append("字段数量较少（<=8个），符合统一参数表特征")
        
        has_code_field = any(f.get('field_name', '').upper().endswith('CODE') for f in fields)
        has_name_field = any(f.get('field_name', '').upper().endswith('NAME') for f in fields)
        
        if has_code_field and has_name_field:
            score += 0.1
            reasons.append("包含CODE-NAME字段对，符合统一参数表模式")
        
        has_value_field = any(f.get('field_name', '').upper().endswith('VALUE') for f in fields)
        if has_value_field:
            score += 0.05
            reasons.append("包含VALUE字段，适合统一参数表存储")
        
        score = min(score, 0.95)
        
        if score >= 0.7:
            suggestions.append(f"建议统一到SIMPLELIST表，INDEXID推荐：{table_info.get('table_name', '').upper()}")
            suggestions.append("可通过配置INDEXID实现快速复用，无需修改代码")
            suggestions.append("建议配置自定义列名映射，提升业务可读性")
        elif score >= 0.5:
            suggestions.append("部分符合统一参数表特征，建议进一步评估")
            suggestions.append("可考虑部分字段统一，部分字段定制")
        else:
            suggestions.append("不建议统一到SIMPLELIST表")
            suggestions.append("字段结构复杂，建议采用定制化开发模式")
        
        return {
            "success": True,
            "confidence": round(score, 2),
            "result": f"统一可行性评分：{round(score * 100, 1)}%",
            "details": {
                "score": round(score, 2),
                "score_details": reasons,
                "suggestions": suggestions,
                "recommendation": "统一到SIMPLELIST表" if score >= 0.7 else "建议定制化开发"
            }
        }
    
    def _mock_normalization_analysis(self, prompt, kwargs):
        fields = kwargs.get('fields', [])
        issues = []
        
        for field in fields:
            field_name = field.get('field_name', '')
            field_type = field.get('field_type', '')
            control_type = field.get('control_type', '')
            length = field.get('length', '')
            
            if not field_name.isupper() and '_' not in field_name:
                issues.append({
                    "field": field_name,
                    "type": "命名规范",
                    "severity": "warning",
                    "message": f"字段名 '{field_name}' 建议使用大写字母加下划线命名（如 PARAM_CODE）",
                    "suggestion": f"建议修改为 '{field_name.upper()}' 或 '{field_name.replace('_', '').upper()}'"
                })
            
            type_mapping = {
                'string': ['input', 'select', 'textarea'],
                'integer': ['input', 'select'],
                'decimal': ['input'],
                'date': ['datepicker'],
                'datetime': ['datepicker'],
                'boolean': ['radio', 'checkbox'],
                'text': ['textarea']
            }
            
            if field_type in type_mapping and control_type not in type_mapping[field_type]:
                issues.append({
                    "field": field_name,
                    "type": "类型匹配",
                    "severity": "error",
                    "message": f"字段类型 '{field_type}' 与控件类型 '{control_type}' 不匹配",
                    "suggestion": f"建议控件类型改为：{', '.join(type_mapping[field_type])}"
                })
            
            if field_type == 'string' and length:
                try:
                    len_int = int(length)
                    if len_int > 2000:
                        issues.append({
                            "field": field_name,
                            "type": "长度设置",
                            "severity": "warning",
                            "message": f"字符串长度 {len_int} 过大，建议使用 text 类型",
                            "suggestion": "建议将字段类型改为 text"
                        })
                    elif len_int < 10 and field_name.upper().endswith('NAME'):
                        issues.append({
                            "field": field_name,
                            "type": "长度设置",
                            "severity": "warning",
                            "message": f"名称字段长度 {len_int} 过小，建议至少50",
                            "suggestion": "建议将长度改为50或更大"
                        })
                except ValueError:
                    pass
        
        if not issues:
            return {
                "success": True,
                "confidence": 0.95,
                "result": "字段定义符合规范，未发现问题",
                "details": {
                    "issues_count": 0,
                    "issues": [],
                    "summary": "所有字段定义均符合规范"
                }
            }
        
        error_count = sum(1 for i in issues if i['severity'] == 'error')
        warning_count = sum(1 for i in issues if i['severity'] == 'warning')
        
        return {
            "success": True,
            "confidence": round(0.9 - len(issues) * 0.02, 2),
            "result": f"发现 {error_count} 个错误，{warning_count} 个警告",
            "details": {
                "issues_count": len(issues),
                "error_count": error_count,
                "warning_count": warning_count,
                "issues": issues,
                "summary": f"共发现 {len(issues)} 个问题，建议修复后重新检查"
            }
        }
    
    def _mock_task_document_generation(self, prompt, kwargs):
        requirement = kwargs.get('requirement', {})
        fields = kwargs.get('fields', [])
        
        title = requirement.get('title', '参数表开发任务书')
        req_no = requirement.get('requirement_no', 'REQ-000')
        
        field_table = "|字段名|类型|长度|是否必填|控件类型|\n|------|----|----|--------|--------|\n"
        for field in fields:
            field_table += f"|{field.get('field_name', '')}|{field.get('field_type', '')}|{field.get('length', '')}|{'是' if field.get('is_required') else '否'}|{field.get('control_type', '')}|\n"
        
        content = f"""## {title}

### 1. 需求概述
{requirement.get('business_description', '暂无业务说明')}

### 2. 需求信息
- 需求编号：{req_no}
- 需求类型：{requirement.get('requirement_type', '新增')}
- 业务领域：{requirement.get('domain', '')}
- 创建人：{requirement.get('requester', '')}

### 3. 字段定义
{field_table}

### 4. 校验规则
{self._generate_validation_rules(fields)}

### 5. 技术要求
- 前端控件需与字段类型匹配
- 存储方式：{', '.join(set(f.get('storage_type', 'code_only') for f in fields))}
- 支持业务参数的动态增删改查

### 6. 测试要点
- 字段类型正确性验证
- 必填字段校验
- 长度限制验证
- 特殊字符处理

### 7. 交付物
- 数据库DDL脚本
- 前端配置文件
- 测试用例文档
"""
        
        return {
            "success": True,
            "confidence": 0.88,
            "result": "任务书生成完成",
            "details": {
                "content": content,
                "word_count": len(content),
                "field_count": len(fields),
                "sections": ["需求概述", "需求信息", "字段定义", "校验规则", "技术要求", "测试要点", "交付物"]
            }
        }
    
    def _generate_validation_rules(self, fields):
        rules = []
        for field in fields:
            if field.get('is_required'):
                rules.append(f"- {field.get('field_name')}：必填")
            if field.get('validation_rule'):
                rules.append(f"- {field.get('field_name')}：{field.get('validation_rule')}")
        return "\n".join(rules) if rules else "- 暂无特殊校验规则"
    
    def _mock_test_case_generation(self, prompt, kwargs):
        requirement = kwargs.get('requirement', {})
        fields = kwargs.get('fields', [])
        
        cases = []
        
        for field in fields:
            field_name = field.get('field_name', '')
            field_type = field.get('field_type', '')
            
            cases.append({
                "case_no": f"TC-{field_name[:10]}",
                "title": f"{field_name}正常录入",
                "case_type": "normal",
                "preconditions": "参数表已创建，表单已加载",
                "steps": f"1. 进入参数配置页面\n2. 输入{field_name}的有效值\n3. 点击保存",
                "expected_result": "保存成功，数据入库",
                "priority": "high"
            })
            
            cases.append({
                "case_no": f"TC-{field_name[:10]}-BOUND",
                "title": f"{field_name}边界值测试",
                "case_type": "boundary",
                "preconditions": "参数表已创建，表单已加载",
                "steps": f"1. 输入{field_name}的最大长度值\n2. 输入{field_name}的最小长度值",
                "expected_result": "边界值数据保存成功",
                "priority": "medium"
            })
            
            if field.get('is_required'):
                cases.append({
                    "case_no": f"TC-{field_name[:10]}-EMPTY",
                    "title": f"{field_name}为空验证",
                    "case_type": "exception",
                    "preconditions": "参数表已创建，表单已加载",
                    "steps": f"1. {field_name}字段留空\n2. 点击保存",
                    "expected_result": "系统提示该字段为必填项",
                    "priority": "high"
                })
        
        return {
            "success": True,
            "confidence": 0.85,
            "result": f"生成了 {len(cases)} 条测试用例",
            "details": {
                "total_cases": len(cases),
                "normal_count": sum(1 for c in cases if c['case_type'] == 'normal'),
                "boundary_count": sum(1 for c in cases if c['case_type'] == 'boundary'),
                "exception_count": sum(1 for c in cases if c['case_type'] == 'exception'),
                "cases": cases
            }
        }
    
    def _mock_sql_generation(self, prompt, kwargs):
        table_info = kwargs.get('table_info', {})
        table_name = table_info.get('table_name', 'parameter_parametertable')
        
        sql_patterns = {
            '查询': f"SELECT * FROM {table_name}",
            '统计': f"SELECT status, COUNT(*) FROM {table_name} GROUP BY status",
            '新增': f"INSERT INTO {table_name} (name, business_description, domain) VALUES ('NEW_TABLE', '新参数表', '业务运营')",
            '更新': f"UPDATE {table_name} SET status = 'active' WHERE id = 1",
            '删除': f"DELETE FROM {table_name} WHERE id = 1"
        }
        
        sql = sql_patterns.get('查询', f"SELECT * FROM {table_name}")
        for key, val in sql_patterns.items():
            if key in prompt:
                sql = val
                break
        
        return {
            "success": True,
            "confidence": 0.82,
            "result": "SQL语句生成完成",
            "details": {
                "sql": sql,
                "table": table_name,
                "type": "SELECT" if "SELECT" in sql else ("INSERT" if "INSERT" in sql else ("UPDATE" if "UPDATE" in sql else "DELETE"))
            }
        }

ai_client = MockAIClient()