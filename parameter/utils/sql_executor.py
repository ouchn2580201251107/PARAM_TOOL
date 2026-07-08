"""
SQL执行工具
提供SQL脚本执行功能，支持SELECT、INSERT、UPDATE、DELETE等操作
"""
import logging
from django.db import connection

logger = logging.getLogger(__name__)


def execute_sql(sql):
    """
    执行SQL脚本
    
    Args:
        sql: SQL语句字符串
        
    Returns:
        dict: 执行结果，包含成功标志、结果集、影响行数等
    """
    logger.info(f"[execute_sql] 开始执行SQL，长度: {len(sql)}")
    
    try:
        sql_type = sql.strip().upper().split()[0]
        
        if sql_type in ('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN'):
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = {
                    'success': True,
                    'type': 'query',
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows),
                }
                logger.info(f"[execute_sql] 查询成功，返回 {len(rows)} 行数据")
                return result
        else:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows_affected = cursor.rowcount
                result = {
                    'success': True,
                    'type': 'update',
                    'rows_affected': rows_affected,
                }
                logger.info(f"[execute_sql] 执行成功，影响 {rows_affected} 行")
                return result
    except Exception as e:
        logger.error(f"[execute_sql] SQL执行失败: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }
