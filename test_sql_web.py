import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'param_tool.settings')

import django
django.setup()

from django.test import Client, override_settings

@override_settings(DEBUG=True)
def test_sql_web_query(query):
    client = Client(enforce_csrf_checks=False)
    
    response = client.post('/sql-manager/', {
        'query': query,
    })
    
    html = response.content.decode('utf-8')
    
    if '查询成功' in html:
        print(f"\n✅ SQL查询成功: {query[:50]}...")
        start = html.find('返回')
        end = html.find('条记录')
        if start != -1 and end != -1:
            count = html[start+2:end].strip()
            print(f"   返回 {count} 条记录")
    elif '执行成功' in html:
        print(f"\n✅ SQL执行成功: {query[:50]}...")
    elif 'error-message' in html:
        start = html.find('error-message">') + 15
        end = html.find('</div>', start)
        error = html[start:end].strip()
        print(f"\n❌ SQL执行失败: {error}")
    else:
        print(f"\n⚠️ 查询结果未知")

print("测试前端SQL查询功能...")

test_sql_web_query("SELECT * FROM parameter_parametertable LIMIT 3")
test_sql_web_query("SELECT status, COUNT(*) FROM parameter_requirement GROUP BY status")
test_sql_web_query("SELECT name, domain, status FROM parameter_parametertable WHERE status = 'active'")
test_sql_web_query("SELECT * FROM parameter_indexidconfig")
test_sql_web_query("SELECT COUNT(*) FROM parameter_fielddefinition")