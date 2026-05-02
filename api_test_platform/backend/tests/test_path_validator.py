"""路径参数命名验证测试"""
import sys
sys.path.insert(0, 'f:/AutoTest/api_test_platform/backend')

from app.utils.path_validator import PathValidator


def test_path_validator():
    test_cases = [
        ('/api/envs/{env_id}', True, '下划线命名'),
        ('/api/envs/{envId}', True, '驼峰命名'),
        ('/api/users/{user_id}/posts/{post_id}', True, '多个下划线参数'),
        ('/api/{serviceId}/{env_id}', True, '混合命名'),
        ('/api/{id}', True, '简单命名'),
        ('/api/{123id}', False, '数字开头'),
        ('/api/{_id}', False, '下划线开头'),
    ]

    print('Path Param Validation Test')
    print('=' * 60)
    all_passed = True
    for path, expected, desc in test_cases:
        valid, error = PathValidator.validate(path)
        passed = (valid == expected)
        if not passed:
            all_passed = False
        status = 'PASS' if passed else 'FAIL'
        print(f'{path} [{desc}]')
        print(f'  Expected: {expected}, Got: {valid}')
        if error:
            print(f'  Error: {error}')
        print(f'  Status: {status}')
        print()

    print('=' * 60)
    print(f'All tests passed: {all_passed}')
    return all_passed


if __name__ == '__main__':
    test_path_validator()
