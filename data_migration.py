import os
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'param_tool.settings')

import django
django.setup()

from parameter.models import ParameterTable, Requirement, RequirementFieldConfig, FieldDefinition

CHINESE_TO_ENGLISH_MAP = {
    '包装种类': 'PACKAGING_TYPE',
    '运输方式': 'TRANSPORT_MODE',
    '监管方式': 'SUPERVISION_MODE',
    '成交方式': 'TRADING_MODE',
    '国别地区': 'COUNTRY_REGION',
    '币制': 'CURRENCY',
    '征免性质': 'TAX_NATURE',
    '计量单位': 'UNIT_MEASURE',
    '港口': 'PORT',
    '海关关区': 'CUSTOMS_DISTRICT',
    '包装类型': 'PACKAGING_TYPE',
    '船舶类型': 'SHIP_TYPE',
    '船舶种类': 'SHIP_CATEGORY',
    '运输类型': 'TRANSPORT_TYPE',
    '关联原因': 'RELATION_REASON',
    '地区': 'REGION',
    '内陆港口': 'INLAND_PORT',
    '海关综合体': 'CUSTOMS_COMPLEX',
    '货物属性': 'CARGO_ATTR',
    '货物类型': 'CARGO_TYPE',
    '集装箱规格': 'CONTAINER_SPEC',
    '贸易方式': 'TRADE_MODE',
    '检验检疫机构': 'CIQ_INSTITUTION',
    '许可证类型': 'LICENSE_TYPE',
    '船舶目的': 'SHIP_PURPOSE',
    '出口许可证': 'EXPORT_LICENSE',
    '进口许可证': 'IMPORT_LICENSE',
    '企业类型': 'ENTERPRISE_TYPE',
    '商品要素': 'PRODUCT_ELEMENT',
    '许可证单证': 'LICENSE_DOC',
    '危险品包装': 'HAZARD_PACKAGING',
    '船舶物料': 'SHIP_SUPPLIES',
    '性别': 'GENDER',
    '用途': 'PURPOSE',
    '原产地': 'ORIGIN',
    '征免类型': 'TAX_TYPE',
    '证书类型': 'CERT_TYPE',
    '计征模式': 'TAX_MODE',
    '证件种类': 'DOC_TYPE',
    '资质管理部门': 'QUALIFICATION_DEPT',
    '农产品目录': 'AGRICULTURE_CATALOG',
    'HS-CIQ编码对照': 'HS_CIQ_MAPPING',
    '代码表': '_CODE_TABLE',
    '映射代码表': '_MAPPING_TABLE',
    '代码表(海关)': '_CUSTOMS_CODE_TABLE',
    '代码表1': '_CODE_TABLE_1',
    '代码表2': '_CODE_TABLE_2',
    '参数表': '_PARAM_TABLE',
    '映射': '_MAPPING',
    '开发': '',
    '表': '_TABLE',
}

def chinese_to_english(name):
    name = name.replace('开发', '')
    name = name.replace('（', '(')
    name = name.replace('）', ')')
    
    for key, value in sorted(CHINESE_TO_ENGLISH_MAP.items(), key=lambda x: -len(x[0])):
        name = name.replace(key, value)
    
    name = re.sub(r'_{2,}', '_', name)
    name = name.strip('_')
    
    if not name:
        name = 'UNKNOWN_TABLE'
    
    if not re.match(r'^[A-Z_0-9]+$', name):
        remaining_chinese = re.findall(r'[\u4e00-\u9fff]+', name)
        for chinese in remaining_chinese:
            pinyin_map = {
                '包装': 'PACKAGING',
                '种类': 'TYPE',
                '方式': 'MODE',
                '性质': 'NATURE',
                '单位': 'UNIT',
                '地区': 'REGION',
                '关区': 'DISTRICT',
                '类型': 'TYPE',
                '船舶': 'SHIP',
                '目的': 'PURPOSE',
                '商品': 'PRODUCT',
                '要素': 'ELEMENT',
                '单证': 'DOC',
                '危险品': 'HAZARD',
                '物料': 'SUPPLIES',
                '用途': 'PURPOSE',
                '产地': 'ORIGIN',
                '证书': 'CERT',
                '证件': 'DOC',
                '资质': 'QUALIFICATION',
                '部门': 'DEPT',
                '目录': 'CATALOG',
                '编码': 'CODE',
                '对照': 'MAPPING',
                '海关': 'CUSTOMS',
                '综合': 'COMPLEX',
                '成交': 'TRADING',
                '监管': 'SUPERVISION',
                '运输': 'TRANSPORT',
                '币制': 'CURRENCY',
                '征免': 'TAX',
                '计量': 'MEASURE',
                '港口': 'PORT',
                '关联': 'RELATION',
                '原因': 'REASON',
                '内陆': 'INLAND',
                '货物': 'CARGO',
                '属性': 'ATTR',
                '集装箱': 'CONTAINER',
                '规格': 'SPEC',
                '贸易': 'TRADE',
                '检验检疫': 'CIQ',
                '机构': 'INSTITUTION',
                '许可证': 'LICENSE',
                '出口': 'EXPORT',
                '进口': 'IMPORT',
                '企业': 'ENTERPRISE',
                '包装': 'PACKAGING',
                '性别': 'GENDER',
                '计征': 'TAX',
                '模式': 'MODE',
                '农产品': 'AGRICULTURE',
                '参数': 'PARAM',
                '映射': 'MAPPING',
            }
            for cn, en in pinyin_map.items():
                if cn in chinese:
                    name = name.replace(cn, en)
                    break
        
        name = re.sub(r'[\u4e00-\u9fff]+', '_UNKNOWN_', name)
        name = re.sub(r'_{2,}', '_', name)
        name = name.strip('_')
    
    return name

def migrate_table_names():
    tables = ParameterTable.objects.all()
    print(f"需要迁移的参数表数量: {tables.count()}")
    
    for table in tables:
        english_name = chinese_to_english(table.name)
        table.name_en = english_name
        table.save()
        print(f"迁移成功: {table.name} -> {english_name}")
    
    print("参数表名称迁移完成！")

def copy_field_configs():
    requirements = Requirement.objects.all()
    print(f"需求总数: {requirements.count()}")
    
    for req in requirements:
        if req.parameter_table:
            existing_configs = RequirementFieldConfig.objects.filter(requirement_id=req.id)
            if existing_configs.count() == 0:
                table_fields = FieldDefinition.objects.filter(parameter_table_id=req.parameter_table_id).order_by('sort_order')
                print(f"需求 '{req.title}' 关联参数表 '{req.parameter_table.name}', 正在复制 {table_fields.count()} 个字段...")
                
                for field in table_fields:
                    RequirementFieldConfig.objects.create(
                        requirement=req,
                        field_definition=field,
                        field_name=field.field_name,
                        display_name=field.display_name,
                        field_type=field.field_type,
                        length=field.length,
                        decimal_places=field.decimal_places,
                        control_type=field.control_type,
                        storage_type=field.storage_type,
                        is_visible=field.is_visible,
                        is_required=field.is_required,
                        validation_rule=field.validation_rule,
                        sort_order=field.sort_order,
                        is_confirmed=True,
                    )
                print(f"字段配置复制完成: {req.title}")
            else:
                print(f"需求 '{req.title}' 已有字段配置，跳过")
        else:
            print(f"需求 '{req.title}' 未关联参数表，跳过")
    
    print("字段配置复制完成！")

if __name__ == '__main__':
    print("=" * 60)
    print("数据迁移脚本")
    print("=" * 60)
    print()
    
    print("1. 迁移参数表英文名称...")
    migrate_table_names()
    print()
    
    print("2. 复制字段配置...")
    copy_field_configs()
    print()
    
    print("=" * 60)
    print("所有数据迁移完成！")
    print("=" * 60)
