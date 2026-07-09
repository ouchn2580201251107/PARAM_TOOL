"""
分页工具模块
提供通用的分页功能
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class PaginationHelper:
    """
    分页辅助类
    简化Django分页操作，生成分页数据供模板使用
    """
    
    def __init__(self, queryset, page_number, page_size=10):
        """
        初始化分页
        :param queryset: 查询集或列表
        :param page_number: 当前页码
        :param page_size: 每页大小，默认为10
        """
        self.paginator = Paginator(queryset, page_size)
        self.page_number = page_number
        self.page_size = page_size
        
        try:
            self.page = self.paginator.page(page_number)
        except PageNotAnInteger:
            self.page = self.paginator.page(1)
        except EmptyPage:
            self.page = self.paginator.page(self.paginator.num_pages)
    
    @property
    def has_previous(self):
        return self.page.has_previous()
    
    @property
    def has_next(self):
        return self.page.has_next()
    
    @property
    def current_page(self):
        return self.page.number
    
    @property
    def total_pages(self):
        return self.paginator.num_pages
    
    @property
    def total_items(self):
        return self.paginator.count
    
    @property
    def previous_page_number(self):
        if self.has_previous:
            return self.page.previous_page_number()
        return None
    
    @property
    def next_page_number(self):
        if self.has_next:
            return self.page.next_page_number()
        return None
    
    @property
    def page_range(self):
        """
        生成显示的页码范围
        最多显示10个页码，当前页居中
        """
        total = self.total_pages
        current = self.current_page
        max_display = 10
        
        if total <= max_display:
            return range(1, total + 1)
        
        half = max_display // 2
        start = max(1, current - half)
        end = min(total, current + half)
        
        if end - start < max_display - 1:
            if start == 1:
                end = min(total, max_display)
            elif end == total:
                start = max(1, total - max_display + 1)
        
        result = []
        if start > 1:
            result.append(1)
            if start > 2:
                result.append('...')
        
        result.extend(range(start, end + 1))
        
        if end < total:
            if end < total - 1:
                result.append('...')
            result.append(total)
        
        return result
    
    @property
    def query_params(self):
        return {}
    
    def set_query_params(self, params):
        """
        设置查询参数，用于分页链接中保留其他参数
        """
        self._query_params = params
    
    @property
    def items(self):
        return self.page.object_list
    
    def to_dict(self):
        """
        返回分页信息字典，供模板使用
        """
        return {
            'has_previous': self.has_previous,
            'has_next': self.has_next,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'total_items': self.total_items,
            'previous_page_number': self.previous_page_number,
            'next_page_number': self.next_page_number,
            'page_range': self.page_range,
            'query_params': getattr(self, '_query_params', {}),
        }


def paginate_queryset(request, queryset, page_size=10):
    """
    便捷函数：根据request获取分页数据
    
    :param request: HTTP请求对象
    :param queryset: 查询集或列表
    :param page_size: 每页大小（默认值，可被request中的page_size覆盖）
    :return: (分页数据, 当前页对象列表)
    """
    page_number = request.GET.get('page', 1)
    
    request_page_size = request.GET.get('page_size')
    if request_page_size and request_page_size.isdigit():
        page_size = int(request_page_size)
    
    helper = PaginationHelper(queryset, page_number, page_size)
    
    query_params = {}
    for key, value in request.GET.items():
        if key != 'page':
            query_params[key] = value
    helper.set_query_params(query_params)
    
    pagination_data = helper.to_dict()
    pagination_data['page_size'] = page_size
    pagination_data['page_size_options'] = [10, 20, 50, 100]
    
    return pagination_data, helper.items