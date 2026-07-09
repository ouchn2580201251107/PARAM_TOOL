"""
自定义模板过滤器
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    获取字典中的值
    """
    return dictionary.get(key)


@register.filter
def get_pass_rate_color(pass_rate):
    """
    根据通过率返回平滑过渡的颜色
    100% - 70%: 绿色渐变 (#27ae60 → #2ecc71)
    70% - 30%: 黄色渐变 (#f39c12 → #f1c40f)
    30% - 0%: 红色渐变 (#e74c3c → #c0392b)
    """
    try:
        rate = float(pass_rate)
    except (ValueError, TypeError):
        return '#95a5a6'
    
    if rate >= 70:
        ratio = (rate - 70) / 30
        r = int(45 + ratio * 46)
        g = int(174 + ratio * 68)
        b = int(96 + ratio * 5)
    elif rate >= 30:
        ratio = (rate - 30) / 40
        r = int(243 - ratio * 11)
        g = int(156 + ratio * 92)
        b = int(18 + ratio * 41)
    else:
        ratio = rate / 30
        r = int(192 + ratio * 85)
        g = int(57 + ratio * 137)
        b = int(43 + ratio * 53)
    
    return f'#{r:02x}{g:02x}{b:02x}'