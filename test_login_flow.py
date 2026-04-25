#!/usr/bin/env python3
"""模拟前端登录流程测试"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("模拟前端登录流程测试")
print("=" * 60)

# 1. 测试管理员登录
print("\n【1】测试管理员登录")
print("-" * 60)
admin_login_data = {
    "id": "admin",
    "password": "admin123"
}
print(f"请求数据: {json.dumps(admin_login_data, ensure_ascii=False)}")

try:
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=admin_login_data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 登录成功!")
        print(f"access_token: {result['access_token'][:50]}...")
        print(f"refresh_token: {result['refresh_token'][:50]}...")

        # 2. 测试获取用户信息
        print("\n【2】测试获取当前用户信息")
        print("-" * 60)
        token = result['access_token']
        headers = {"Authorization": f"Bearer {token}"}

        me_response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"状态码: {me_response.status_code}")

        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ 获取用户信息成功!")
            print(f"  用户ID: {user_info['id']}")
            print(f"  用户名: {user_info['username']}")
            print(f"  真实姓名: {user_info['real_name']}")
            print(f"  角色: {user_info['role']}")
            print(f"  院系: {user_info['department']}")
        else:
            print(f"❌ 获取用户信息失败: {me_response.text}")
    else:
        print(f"❌ 登录失败: {response.text}")
except Exception as e:
    print(f"❌ 请求异常: {e}")

# 3. 测试学生登录
print("\n\n【3】测试学生登录")
print("-" * 60)
student_login_data = {
    "id": "2021001",
    "password": "123456"
}
print(f"请求数据: {json.dumps(student_login_data, ensure_ascii=False)}")

try:
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=student_login_data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 登录成功!")
        print(f"access_token: {result['access_token'][:50]}...")

        # 获取学生用户信息
        token = result['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)

        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ 获取用户信息成功!")
            print(f"  用户ID: {user_info['id']}")
            print(f"  用户名: {user_info['username']}")
            print(f"  真实姓名: {user_info['real_name']}")
            print(f"  角色: {user_info['role']}")
    else:
        print(f"❌ 登录失败: {response.text}")
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
print("\n📝 前端登录页面账号信息:")
print("-" * 60)
print("【管理员账号】")
print("  学号/工号: admin")
print("  密码: admin123")
print()
print("【学生账号】")
print("  学号/工号: 2021001")
print("  密码: 123456")
print("-" * 60)
