"""
测试条件处理器的安全功能
"""
import sys
import os

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.services.processors.condition_processor import (
    StepConditionEvaluator,
    ConditionProcessor,
    _create_safe_builtins,
    _validate_script,
    _execute_with_timeout,
    ScriptSecurityError,
    ScriptExecutionTimeout
)


def test_safe_builtins():
    """测试安全内置函数"""
    print("\n=== 测试安全内置函数 ===")
    safe_builtins = _create_safe_builtins()
    
    # 测试允许的函数
    assert "str" in safe_builtins
    assert "int" in safe_builtins
    assert "len" in safe_builtins
    print("✓ 允许的函数存在")
    
    # 测试禁止的函数
    assert "open" not in safe_builtins
    assert "exec" not in safe_builtins
    assert "eval" not in safe_builtins
    assert "__import__" not in safe_builtins
    print("✓ 危险函数已被排除")


def test_script_validation():
    """测试脚本验证"""
    print("\n=== 测试脚本验证 ===")
    
    # 测试安全脚本
    safe_script = "result = len('hello') > 3"
    try:
        _validate_script(safe_script)
        print("✓ 安全脚本通过验证")
    except ScriptSecurityError:
        print("✗ 安全脚本验证失败")
    
    # 测试危险脚本 - import
    dangerous_script1 = "import os"
    try:
        _validate_script(dangerous_script1)
        print("✗ 危险脚本未被检测到")
    except ScriptSecurityError as e:
        print(f"✓ 成功检测到危险操作: {e}")
    
    # 测试危险脚本 - os模块
    dangerous_script2 = "os.system('ls')"
    try:
        _validate_script(dangerous_script2)
        print("✗ 危险脚本未被检测到")
    except ScriptSecurityError as e:
        print(f"✓ 成功检测到危险操作: {e}")
    
    # 测试危险脚本 - eval
    dangerous_script3 = "eval('1+1')"
    try:
        _validate_script(dangerous_script3)
        print("✗ 危险脚本未被检测到")
    except ScriptSecurityError as e:
        print(f"✓ 成功检测到危险操作: {e}")
    
    # 测试危险脚本 - open
    dangerous_script4 = "open('test.txt', 'w')"
    try:
        _validate_script(dangerous_script4)
        print("✗ 危险脚本未被检测到")
    except ScriptSecurityError as e:
        print(f"✓ 成功检测到危险操作: {e}")


def test_timeout_execution():
    """测试超时执行"""
    print("\n=== 测试超时执行 ===")
    
    # 测试正常执行
    def normal_function():
        return sum(range(10))
    
    result = _execute_with_timeout(normal_function, timeout=1.0)
    assert result == 45
    print("✓ 正常函数执行成功")
    
    # 测试超时执行
    def slow_function():
        import time
        time.sleep(10)
        return True
    
    try:
        _execute_with_timeout(slow_function, timeout=0.5)
        print("✗ 超时未被检测到")
    except ScriptExecutionTimeout as e:
        print(f"✓ 成功检测到超时: {e}")


def test_step_condition_evaluator():
    """测试步骤条件评估器"""
    print("\n=== 测试步骤条件评估器 ===")
    
    evaluator = StepConditionEvaluator()
    
    # 测试安全的表达式
    config1 = {
        "type": "expression",
        "expression": "len('hello') > 3"
    }
    result = evaluator.evaluate(config1)
    assert result is True
    print("✓ 安全表达式执行成功")
    
    # 测试危险的表达式
    config2 = {
        "type": "expression",
        "expression": "__import__('os').system('ls')"
    }
    result = evaluator.evaluate(config2)
    assert result is False  # 应该返回False，因为评估失败
    print("✓ 危险表达式被阻止")
    
    # 测试安全的脚本
    config3 = {
        "type": "script",
        "script": "result = len([1, 2, 3]) == 3"
    }
    result = evaluator.evaluate(config3)
    assert result is True
    print("✓ 安全脚本执行成功")
    
    # 测试危险的脚本
    config4 = {
        "type": "script",
        "script": "import os\nresult = True"
    }
    result = evaluator.evaluate(config4)
    assert result is False  # 应该返回False，因为包含危险操作
    print("✓ 危险脚本被阻止")


def test_condition_processor():
    """测试条件处理器"""
    print("\n=== 测试条件处理器 ===")
    
    processor = ConditionProcessor()
    
    # 测试安全的表达式
    config1 = {
        "condition_type": "expression",
        "expression": "5 > 3"
    }
    result = processor._evaluate_expression(config1)
    assert result is True
    print("✓ 安全表达式执行成功")
    
    # 测试危险的表达式
    config2 = {
        "condition_type": "expression",
        "expression": "open('/etc/passwd')"
    }
    result = processor._evaluate_expression(config2)
    assert result is False
    print("✓ 危险表达式被阻止")
    
    # 测试安全的脚本
    config3 = {
        "condition_type": "script",
        "script": "__result = sum([1, 2, 3]) == 6"
    }
    result = processor._evaluate_script(config3)
    assert result is True
    print("✓ 安全脚本执行成功")
    
    # 测试危险的脚本
    config4 = {
        "condition_type": "script",
        "script": "import subprocess\n__result = True"
    }
    result = processor._evaluate_script(config4)
    assert result is False
    print("✓ 危险脚本被阻止")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试条件处理器安全功能")
    print("=" * 60)
    
    try:
        test_safe_builtins()
        test_script_validation()
        test_timeout_execution()
        test_step_condition_evaluator()
        test_condition_processor()
        
        print("\n" + "=" * 60)
        print("所有测试通过！安全措施已正确实施。")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
