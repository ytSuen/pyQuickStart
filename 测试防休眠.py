"""
测试防休眠功能
"""
import time
from power_manager import PowerManager
from logger import Logger

def main():
    logger = Logger()
    pm = PowerManager()
    
    print("=" * 50)
    print("  防休眠功能测试")
    print("=" * 50)
    print()
    
    # 测试启动防休眠
    print("1. 启动防休眠...")
    result = pm.prevent_sleep()
    if result:
        print("   ✓ 防休眠已启动")
        print(f"   - 状态: {pm.is_preventing_sleep}")
        print(f"   - 键盘模拟间隔: {pm._keyboard_simulation_interval}秒")
        print(f"   - API刷新间隔: {pm._keepalive_interval_seconds}秒")
    else:
        print("   ✗ 防休眠启动失败")
        return
    
    print()
    print("2. 等待并观察...")
    print("   程序将运行 3 分钟，观察键盘模拟是否工作")
    print("   请查看日志文件: logs/hotkey_YYYYMMDD.log")
    print()
    
    # 运行3分钟
    for i in range(180):
        time.sleep(1)
        if i % 10 == 0:
            print(f"   已运行 {i} 秒...")
            print(f"   - 防休眠状态: {'开启' if pm.is_preventing_sleep else '关闭'}")
            print(f"   - 键盘模拟定时器: {'运行中' if pm._keyboard_simulation_timer else '未运行'}")
            print(f"   - API刷新定时器: {'运行中' if pm._keepalive_timer else '未运行'}")
    
    print()
    print("3. 关闭防休眠...")
    result = pm.allow_sleep()
    if result:
        print("   ✓ 防休眠已关闭")
    else:
        print("   ✗ 防休眠关闭失败")
    
    print()
    print("=" * 50)
    print("  测试完成")
    print("=" * 50)
    print()
    print("请检查日志文件查看详细信息")

if __name__ == "__main__":
    main()
