#!/usr/bin/env python3
"""
彩虹一号系统快速设置脚本
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def setup_env_file():
    """设置环境变量文件"""
    env_template = ".env.template"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} 已存在，跳过创建")
        return True
    
    if os.path.exists(env_template):
        shutil.copy(env_template, env_file)
        print(f"✅ 已创建 {env_file} 文件")
        print("🔧 请编辑 .env 文件并填入必要的API密钥")
        return True
    else:
        print(f"❌ 未找到 {env_template} 模板文件")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ["reports", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"📁 目录已存在: {directory}")
    
    return True

def test_system():
    """测试系统"""
    print("🧪 测试系统配置...")
    try:
        result = subprocess.run([sys.executable, "main.py", "--mode", "config"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 系统配置检查通过")
            return True
        else:
            print("❌ 系统配置检查失败")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 系统测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🌈 彩虹一号 AI 日报系统 - 快速设置")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 设置环境文件
    if not setup_env_file():
        return 1
    
    # 创建目录
    if not create_directories():
        return 1
    
    # 测试系统
    if not test_system():
        print("\n⚠️  配置检查未通过，请:")
        print("1. 编辑 .env 文件，填入正确的API密钥")
        print("2. 运行 python main.py --mode config 检查配置")
        print("3. 运行 python main.py --mode test 测试飞书连接")
        return 1
    
    print("\n🎉 彩虹一号系统设置完成！")
    print("\n📋 下一步操作:")
    print("1. 编辑 .env 文件配置API密钥")
    print("2. 运行 python main.py --mode test 测试系统")
    print("3. 运行 python main.py --mode once 执行一次任务")
    print("4. 运行 python main.py --mode scheduler 启动定时任务")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 