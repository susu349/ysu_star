"""
初始化地图数据脚本
1. 复制地图瓦片文件
2. 初始化校园POI数据
"""
import os
import shutil
import sys
import uuid
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from campus_ai.core.database import SessionLocal, engine, Base
from campus_ai.models.map import POI


def copy_map_tiles():
    """复制地图瓦片文件"""
    source_dir = Path("/home/su/桌面/智慧地图/haigang_tiles")
    target_dir = Path(__file__).parent.parent / "map_tiles"

    if not source_dir.exists():
        print(f"⚠️  源瓦片目录不存在: {source_dir}")
        print("请先运行地图下载脚本")
        return False

    target_dir.mkdir(exist_ok=True)

    print(f"📋 复制地图瓦片文件...")
    count = 0
    for tile_file in source_dir.glob("*.png"):
        shutil.copy2(tile_file, target_dir / tile_file.name)
        count += 1

    print(f"✅ 成功复制 {count} 个瓦片文件")
    return True


def init_pois(db: Session):
    """初始化校园POI数据"""
    print(f"📋 初始化校园POI数据...")

    # 检查是否已存在数据
    if db.query(POI).count() > 0:
        print("⚠️  POI数据已存在，跳过初始化")
        return

    # 燕山大学校园POI示例数据
    # 坐标基于秦皇岛燕山大学
    ysu_pois = [
        {
            "name": "燕山大学正门",
            "description": "燕山大学主校门，标志性建筑",
            "poi_type": "building",
            "latitude": 39.9085,
            "longitude": 119.5146,
            "address": "河北大街西段438号",
            "tags": ["校门", "标志性建筑"],
            "is_official": True,
        },
        {
            "name": "图书馆",
            "description": "燕山大学图书馆，藏书丰富",
            "poi_type": "building",
            "latitude": 39.9067,
            "longitude": 119.5133,
            "address": "校园中心",
            "tags": ["图书馆", "学习", "自习"],
            "opening_hours": "8:00-22:00",
            "is_official": True,
        },
        {
            "name": "第一教学楼",
            "description": "主要教学楼之一",
            "poi_type": "building",
            "latitude": 39.9075,
            "longitude": 119.5155,
            "tags": ["教学楼", "上课"],
            "is_official": True,
        },
        {
            "name": "第二教学楼",
            "description": "主要教学楼之一",
            "poi_type": "building",
            "latitude": 39.9062,
            "longitude": 119.5158,
            "tags": ["教学楼", "上课"],
            "is_official": True,
        },
        {
            "name": "东区食堂",
            "description": "东区学生食堂，美食丰富",
            "poi_type": "food",
            "latitude": 39.9089,
            "longitude": 119.5172,
            "tags": ["食堂", "美食"],
            "opening_hours": "6:30-21:00",
            "is_official": True,
        },
        {
            "name": "西区食堂",
            "description": "西区学生食堂",
            "poi_type": "food",
            "latitude": 39.9045,
            "longitude": 119.5118,
            "tags": ["食堂", "美食"],
            "opening_hours": "6:30-21:00",
            "is_official": True,
        },
        {
            "name": "体育馆",
            "description": "室内体育馆，运动健身好去处",
            "poi_type": "facility",
            "latitude": 39.9058,
            "longitude": 119.5185,
            "tags": ["体育馆", "运动", "健身"],
            "is_official": True,
        },
        {
            "name": "田径场",
            "description": "标准田径场，跑步运动",
            "poi_type": "facility",
            "latitude": 39.9050,
            "longitude": 119.5195,
            "tags": ["田径场", "跑步", "运动"],
            "is_official": True,
        },
        {
            "name": "燕鸣湖",
            "description": "校园美丽湖泊，风景优美，适合散步",
            "poi_type": "landscape",
            "latitude": 39.9065,
            "longitude": 119.5145,
            "tags": ["湖泊", "风景", "散步"],
            "is_official": True,
        },
        {
            "name": "大学生活动中心",
            "description": "社团活动、文艺演出场所",
            "poi_type": "facility",
            "latitude": 39.9078,
            "longitude": 119.5180,
            "tags": ["活动中心", "社团", "文艺"],
            "is_official": True,
        },
        {
            "name": "工程训练中心",
            "description": "工程实践教学基地",
            "poi_type": "building",
            "latitude": 39.9035,
            "longitude": 119.5125,
            "tags": ["工程训练", "实践"],
            "is_official": True,
        },
        {
            "name": "校医院",
            "description": "校园医疗服务",
            "poi_type": "facility",
            "latitude": 39.9092,
            "longitude": 119.5135,
            "tags": ["医院", "医疗"],
            "opening_hours": "8:00-18:00",
            "is_official": True,
        },
        {
            "name": "东区宿舍",
            "description": "东区学生宿舍区",
            "poi_type": "building",
            "latitude": 39.9098,
            "longitude": 119.5165,
            "tags": ["宿舍", "住宿"],
            "is_official": True,
        },
        {
            "name": "西区宿舍",
            "description": "西区学生宿舍区",
            "poi_type": "building",
            "latitude": 39.9038,
            "longitude": 119.5105,
            "tags": ["宿舍", "住宿"],
            "is_official": True,
        },
        {
            "name": "图书馆广场",
            "description": "图书馆前广场，适合拍照打卡",
            "poi_type": "landscape",
            "latitude": 39.9070,
            "longitude": 119.5128,
            "tags": ["广场", "拍照", "打卡"],
            "is_official": True,
        },
    ]

    for poi_data in ysu_pois:
        poi = POI(
            id=str(uuid.uuid4()),
            **poi_data,
            status="approved",
            check_in_count=0,
            like_count=0,
            favorite_count=0,
            comment_count=0,
            view_count=0,
        )
        db.add(poi)

    db.commit()
    print(f"✅ 成功初始化 {len(ysu_pois)} 个POI")


def main():
    print("🚀 开始初始化地图数据...\n")

    # 1. 复制地图瓦片
    copy_map_tiles()
    print()

    # 2. 初始化POI数据
    db = SessionLocal()
    try:
        init_pois(db)
    finally:
        db.close()

    print("\n🎉 地图数据初始化完成！")


if __name__ == "__main__":
    main()
