"""
测试自动更新功能
"""
from updater import Updater
from logger import Logger

def test_version_compare():
    """测试版本比较"""
    updater = Updater()
    
    print("=== 测试版本比较 ===")
    test_cases = [
        ("1.1.0", "1.0.0", 1),   # 1.1.0 > 1.0.0
        ("1.0.0", "1.0.0", 0),   # 1.0.0 == 1.0.0
        ("1.0.0", "1.1.0", -1),  # 1.0.0 < 1.1.0
        ("2.0.0", "1.9.9", 1),   # 2.0.0 > 1.9.9
        ("1.0.1", "1.0.0", 1),   # 1.0.1 > 1.0.0
    ]
    
    for v1, v2, expected in test_cases:
        result = updater._compare_version(v1, v2)
        status = "✓" if result == expected else "✗"
        print(f"{status} {v1} vs {v2}: {result} (期望: {expected})")

def test_check_update():
    """测试检查更新"""
    updater = Updater()
    logger = Logger()
    
    print("\n=== 测试检查更新 ===")
    print(f"当前版本: {updater.get_current_version()}")
    print("正在检查更新...")
    
    has_update, version_info = updater.check_update()
    
    if has_update:
        print(f"✓ 发现新版本: {version_info['version']}")
        print(f"  下载地址: {version_info['download_url']}")
        print(f"  更新内容: {version_info.get('changelog', '无')}")
    else:
        print("✓ 当前已是最新版本")

def test_version_file():
    """测试版本文件"""
    import json
    from pathlib import Path
    
    print("\n=== 测试版本文件 ===")
    version_file = Path("version.json")
    
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✓ 版本文件存在")
            print(f"  版本号: {data.get('version')}")
            print(f"  构建日期: {data.get('build_date')}")
            print(f"  描述: {data.get('description')}")
    else:
        print("✗ 版本文件不存在")

if __name__ == "__main__":
    print("pyQuickStart 自动更新功能测试\n")
    
    try:
        test_version_file()
        test_version_compare()
        test_check_update()
        
        print("\n=== 测试完成 ===")
        print("如果所有测试都通过，说明更新功能正常工作")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
