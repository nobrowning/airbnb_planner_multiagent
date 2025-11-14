#!/usr/bin/env python3
"""测试 Host Agent 与认证智能体的连接"""

import os
import sys

import httpx
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 配置
AIRBNB_AGENT_URL = os.getenv('AIR_AGENT_URL', 'http://localhost:10002')
AIRBNB_API_KEY = os.getenv('AIRBNB_API_KEY')


def test_airbnb_agent_connection():
    """测试与 Airbnb Agent 的连接"""
    print('\n=== 测试 Airbnb Agent 连接 ===')
    print(f'Agent URL: {AIRBNB_AGENT_URL}')
    print(f'API Key 已设置: {"是" if AIRBNB_API_KEY else "否"}')
    
    if not AIRBNB_API_KEY:
        print('\n⚠️  警告: AIRBNB_API_KEY 未设置')
        print('如果 Airbnb Agent 启用了认证，连接将失败')
        print('请在 .env 文件中设置 AIRBNB_API_KEY')
    
    print('\n--- 测试 1: 获取 Agent Card (无需认证) ---')
    try:
        response = httpx.get(
            f'{AIRBNB_AGENT_URL}/.well-known/agent-card.json',
            timeout=5.0
        )
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            agent_card = response.json()
            print(f'✓ Agent Name: {agent_card.get("name")}')
            print(f'✓ Description: {agent_card.get("description")}')
        else:
            print(f'✗ 失败: {response.text[:200]}')
    except Exception as e:
        print(f'✗ 错误: {e}')
        return False
    
    print('\n--- 测试 2: 不带认证访问根路径 ---')
    try:
        response = httpx.get(f'{AIRBNB_AGENT_URL}/', timeout=5.0)
        print(f'状态码: {response.status_code}')
        if response.status_code == 401:
            print('✓ 预期行为: 未认证请求被拒绝')
            print('这表明 Airbnb Agent 已启用认证')
        elif response.status_code == 200:
            print('ℹ️  Airbnb Agent 未启用认证或允许无认证访问')
        else:
            print(f'响应: {response.text[:200]}')
    except Exception as e:
        print(f'✗ 错误: {e}')
    
    if not AIRBNB_API_KEY:
        print('\n⚠️  跳过认证测试（未设置 API Key）')
        return True
    
    print('\n--- 测试 3: 使用 API Key 访问 ---')
    try:
        headers = {'Authorization': f'Bearer {AIRBNB_API_KEY}'}
        response = httpx.get(
            f'{AIRBNB_AGENT_URL}/',
            headers=headers,
            timeout=5.0
        )
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            print('✓ 认证成功！Host Agent 可以正常连接到 Airbnb Agent')
            return True
        elif response.status_code == 401:
            print('✗ 认证失败：API Key 无效')
            print('请检查 Host Agent 的 AIRBNB_API_KEY 是否与 Airbnb Agent 的 API_KEY 一致')
            return False
        else:
            print(f'✗ 意外响应: {response.text[:200]}')
            return False
    except Exception as e:
        print(f'✗ 错误: {e}')
        return False


def check_host_agent_config():
    """检查 Host Agent 配置"""
    print('\n=== 检查 Host Agent 配置 ===')
    
    configs = {
        'AIR_AGENT_URL': os.getenv('AIR_AGENT_URL'),
        'WEA_AGENT_URL': os.getenv('WEA_AGENT_URL'),
        'TRIP_AGENT_URL': os.getenv('TRIP_AGENT_URL'),
        'AIRBNB_API_KEY': '已设置' if AIRBNB_API_KEY else '未设置',
    }
    
    for key, value in configs.items():
        if value:
            status = '✓' if value != '未设置' else '⚠️ '
            print(f'{status} {key}: {value if key != "AIRBNB_API_KEY" else value}')
        else:
            print(f'✗ {key}: 未设置')


def main():
    """运行所有测试"""
    print('=' * 60)
    print('Host Agent - 远程智能体认证测试')
    print('=' * 60)
    
    check_host_agent_config()
    
    # 测试 Airbnb Agent 连接
    success = test_airbnb_agent_connection()
    
    print('\n' + '=' * 60)
    if success:
        print('✓ 所有测试通过！')
        print('Host Agent 已正确配置，可以与 Airbnb Agent 通信')
    else:
        print('✗ 部分测试失败')
        print('请检查上述错误信息并修复配置')
    print('=' * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
