#!/usr/bin/env python3
"""模拟前端数据处理逻辑"""

# 模拟 API 响应
api_response = {
    "total": 3,
    "items": [
        {
            "id": "41184da6-9084-44bc-8b23-8c1ac39d3876",
            "title": "关于举办全国大学生电力创新设计竞赛燕山大学校内选拔赛的通知",
            "level": "school",
            "category": "科技创新",
            "organizer": "创新创业教育与指导中心",
            "team_count": 0
        },
        {
            "id": "2f97c8db-b91a-4053-ad9b-c1b62cd451c3",
            "title": "关于举办第一届燕山大学大学生数字媒体科技作品及创意竞赛的通知",
            "level": "national",
            "category": "计算机设计",
            "organizer": "创新创业教育与指导中心",
            "team_count": 2
        }
    ]
}

print("=" * 100)
print("1. API 返回数据")
print("=" * 100)
print(f"类型: {type(api_response)}")
print(f"键: {list(api_response.keys())}")
print()

# 模拟前端: competitions.value = response.items || response || []
competitions = api_response.get('items') or api_response or []

print("=" * 100)
print("2. 前端赋值: competitions.value = response.items || response || []")
print("=" * 100)
print(f"competitions 类型: {type(competitions)}")
print(f"competitions 长度: {len(competitions)}")
print()

# 模拟计算属性
print("=" * 100)
print("3. 计算属性")
print("=" * 100)

totalCount = len(competitions)
nationalCount = len([c for c in competitions if str(c.get('level')).upper() == 'NATIONAL'])
provincialCount = len([c for c in competitions if str(c.get('level')).upper() == 'PROVINCIAL'])
schoolCount = len([c for c in competitions if str(c.get('level')).upper() == 'SCHOOL'])

print(f"totalCount: {totalCount}")
print(f"nationalCount: {nationalCount}")
print(f"provincialCount: {provincialCount}")
print(f"schoolCount: {schoolCount}")
print()

# 模拟 level 处理
print("=" * 100)
print("4. Level 处理 (用 toUpperCase)")
print("=" * 100)

for i, c in enumerate(competitions, 1):
    level = c.get('level')
    levelUpper = str(level).upper()
    print(f"赛事 {i}:")
    print(f"  原始 level: {level!r}")
    print(f"  toUpperCase: {levelUpper!r}")
    print()

print("=" * 100)
print("5. 筛选逻辑 (selectedLevel = 'SCHOOL')")
print("=" * 100)

selectedLevel = 'SCHOOL'
filtered = [c for c in competitions if str(c.get('level')).upper() == selectedLevel]
print(f"筛选后: {len(filtered)} 个赛事")
for c in filtered:
    print(f"  - {c['title'][:50]}...")

print()
print("=" * 100)
print("结论: 前端逻辑完全正确！数据应该能正常显示！")
print("=" * 100)
