#!/usr/bin/env python3
"""
安装支付SDK脚本
"""

import subprocess
import sys

def install_package(package_name, import_name=None):
    """安装Python包"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"📦 正在安装 {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 安装失败")
            return False

def main():
    print("=" * 50)
    print("支付SDK安装脚本")
    print("=" * 50)
    
    packages = [
        ("python-alipay-sdk", "alipay"),
        ("wechatpayv3", "wechatpayv3"),
        ("Flask", "flask"),
    ]
    
    results = []
    for package, import_name in packages:
        results.append(install_package(package, import_name))
    
    print("\n" + "=" * 50)
    print("安装结果:")
    print("=" * 50)
    
    all_success = all(results)
    
    if all_success:
        print("\n✅ 所有SDK已安装完成！")
        print("\n现在可以使用真实支付功能了。")
    else:
        print("\n⚠️ 部分SDK安装失败，请手动安装:")
        print("  pip install python-alipay-sdk")
        print("  pip install wechatpayv3")
        print("  pip install Flask")

if __name__ == "__main__":
    main()

