import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'param_tool.settings')

import django
django.setup()

from django.db import connection

def test_sql_query(query):
    print(f"\n{'='*60}")
    print(f"执行SQL: {query}")
    print('='*60)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                
                print(f"\n查询成功，返回 {len(results)} 条记录")
                print(f"\n列名: {', '.join(columns)}")
                print('-' * 60)
                
                for i, row in enumerate(results[:5]):
                    print(f"第{i+1}行: {row}")
                
                if len(results) > 5:
                    print(f"...还有 {len(results) - 5} 条记录")
            else:
                print(f"执行成功，影响 {cursor.rowcount} 行")
                
    except Exception as e:
        print(f"执行失败: {e}")

test_sql_query("SELECT * FROM parameter_parametertable")
test_sql_query("SELECT status, COUNT(*) as count FROM parameter_requirement GROUP BY status")
test_sql_query("SELECT * FROM parameter_testcase WHERE automated = 1")
test_sql_query("SELECT * FROM parameter_metadata LIMIT 5")
test_sql_query("SELECT COUNT(*) FROM parameter_fielddefinition")