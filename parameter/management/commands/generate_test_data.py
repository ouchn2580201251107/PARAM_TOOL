"""
生成测试数据命令
用于生成测试批次和测试结果的模拟数据
"""
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from parameter.models import TestCase, TestBatch, AutomationTestResult, Requirement


class Command(BaseCommand):
    help = '生成测试批次和测试结果的模拟数据'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='清空现有测试数据后重新生成')
    
    def handle(self, *args, **options):
        self.stdout.write('开始生成测试数据...')
        
        if options.get('clear'):
            AutomationTestResult.objects.all().delete()
            TestBatch.objects.all().delete()
            self.stdout.write('已清空现有测试数据')
        
        requirements = Requirement.objects.all()[:5]
        if not requirements.exists():
            self.stdout.write(self.style.WARNING('警告：没有需求数据，需要先创建需求'))
            return
        
        test_cases = TestCase.objects.filter(automated=True)
        if not test_cases.exists():
            for i, req in enumerate(requirements):
                for j in range(1, 6):
                    TestCase.objects.create(
                        requirement=req,
                        case_no=f'TC_{req.requirement_no}_{j:03d}',
                        title=f'{req.title} - 测试用例{j}',
                        case_type=random.choice(['normal', 'boundary', 'exception']),
                        preconditions='系统正常运行',
                        steps='1. 打开页面\n2. 输入数据\n3. 点击提交',
                        expected_result='操作成功',
                        status='automated',
                        automated=True,
                    )
            test_cases = TestCase.objects.filter(automated=True)
            self.stdout.write(f'已创建 {test_cases.count()} 条自动化测试用例')
        
        batches_to_create = [
            {'batch_no': 'BATCH_20260615_001', 'description': '单元测试 - 基础模块', 'pass_rate': 95.2},
            {'batch_no': 'BATCH_20260620_002', 'description': '集成测试 - 接口联调', 'pass_rate': 72.8},
            {'batch_no': 'BATCH_20260625_003', 'description': '回归测试 - 版本1.0', 'pass_rate': 88.5},
            {'batch_no': 'BATCH_20260628_004', 'description': '性能测试 - 压力测试', 'pass_rate': 65.3},
            {'batch_no': 'BATCH_20260701_005', 'description': '功能测试 - 参数表模块', 'pass_rate': 91.7},
            {'batch_no': 'BATCH_20260703_006', 'description': '冒烟测试 - 紧急修复', 'pass_rate': 100.0},
            {'batch_no': 'BATCH_20260705_007', 'description': '回归测试 - 全量', 'pass_rate': 82.4},
            {'batch_no': 'BATCH_20260706_008', 'description': '边界测试 - 异常场景', 'pass_rate': 45.6},
            {'batch_no': 'BATCH_20260707_009', 'description': '安全测试 - 权限验证', 'pass_rate': 98.1},
            {'batch_no': 'BATCH_20260708_010', 'description': '综合测试 - 发布前验证', 'pass_rate': 89.3},
            {'batch_no': 'BATCH_20260709_011', 'description': '兼容性测试 - 多浏览器', 'pass_rate': 55.8},
            {'batch_no': 'BATCH_20260710_012', 'description': '验收测试 - 用户验证', 'pass_rate': 76.2},
        ]
        
        base_time = datetime.now() - timedelta(days=25)
        
        for idx, batch_info in enumerate(batches_to_create):
            total_cases = test_cases.count()
            pass_count = round(total_cases * batch_info['pass_rate'] / 100)
            fail_count = total_cases - pass_count - random.randint(0, 2)
            skip_count = total_cases - pass_count - fail_count
            
            if skip_count < 0:
                skip_count = 0
                fail_count = total_cases - pass_count
            
            batch = TestBatch.objects.create(
                batch_no=batch_info['batch_no'],
                description=batch_info['description'],
                status='completed',
                total_cases=total_cases,
                passed_count=pass_count,
                failed_count=fail_count,
                skipped_count=skip_count,
                current_progress=100,
                start_time=base_time + timedelta(days=idx * 2, hours=idx * 3),
                end_time=base_time + timedelta(days=idx * 2, hours=idx * 3, minutes=30),
                duration=1800 + idx * 600,
                created_at=base_time + timedelta(days=idx * 2),
            )
            
            case_list = list(test_cases)
            random.shuffle(case_list)
            
            passed_cases = case_list[:pass_count]
            failed_cases = case_list[pass_count:pass_count + fail_count]
            skipped_cases = case_list[pass_count + fail_count:pass_count + fail_count + skip_count]
            
            for case in passed_cases:
                AutomationTestResult.objects.create(
                    test_batch=batch,
                    test_case=case,
                    status='passed',
                    execution_date=batch.start_time + timedelta(seconds=random.randint(0, 1800)),
                    duration=round(random.uniform(0.5, 2.0), 2),
                )
            
            for case in failed_cases:
                AutomationTestResult.objects.create(
                    test_batch=batch,
                    test_case=case,
                    status='failed',
                    error_message=f'断言失败：预期结果与实际结果不匹配 - {case.title}',
                    execution_date=batch.start_time + timedelta(seconds=random.randint(0, 1800)),
                    duration=round(random.uniform(0.5, 2.0), 2),
                )
            
            for case in skipped_cases:
                AutomationTestResult.objects.create(
                    test_batch=batch,
                    test_case=case,
                    status='skipped',
                    error_message='用例被跳过：前置条件不满足',
                    execution_date=batch.start_time + timedelta(seconds=random.randint(0, 1800)),
                    duration=0.0,
                )
            
            self.stdout.write(f'已创建测试批次: {batch.batch_no} (通过率: {batch_info["pass_rate"]}%)')
        
        self.stdout.write(self.style.SUCCESS('测试数据生成完成！'))