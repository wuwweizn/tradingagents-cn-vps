"""
点数套餐管理器
用于管理点数套餐配置和购买记录
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PointsPackageManager:
    """点数套餐管理器"""
    
    def __init__(self):
        # 配置文件路径
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.packages_file = config_dir / "points_packages.json"
        self.orders_file = config_dir / "points_orders.json"
        
        # 默认套餐配置
        self.default_packages = [
            {
                "id": "basic",
                "name": "基础套餐",
                "points": 100,
                "price": 10.0,
                "currency": "CNY",
                "description": "适合偶尔使用的用户",
                "enabled": True,
                "bonus": 0  # 赠送点数
            },
            {
                "id": "standard",
                "name": "标准套餐",
                "points": 500,
                "price": 45.0,
                "currency": "CNY",
                "description": "性价比最高的选择",
                "enabled": True,
                "bonus": 50  # 赠送50点
            },
            {
                "id": "premium",
                "name": "高级套餐",
                "points": 1000,
                "price": 80.0,
                "currency": "CNY",
                "description": "适合重度用户",
                "enabled": True,
                "bonus": 150  # 赠送150点
            },
            {
                "id": "vip",
                "name": "VIP套餐",
                "points": 3000,
                "price": 200.0,
                "currency": "CNY",
                "description": "最超值的长期选择",
                "enabled": True,
                "bonus": 500  # 赠送500点
            }
        ]
        
        # 确保配置文件存在
        self._ensure_packages_file()
        self._ensure_orders_file()
    
    def _ensure_packages_file(self):
        """确保套餐配置文件存在"""
        if not self.packages_file.exists():
            self._save_packages(self.default_packages.copy())
            logger.info(f"✅ 创建默认点数套餐配置文件: {self.packages_file}")
    
    def _ensure_orders_file(self):
        """确保订单文件存在"""
        if not self.orders_file.exists():
            self._save_orders([])
            logger.info(f"✅ 创建订单文件: {self.orders_file}")
    
    def _load_packages(self) -> List[Dict]:
        """加载套餐配置"""
        try:
            if self.packages_file.exists():
                with open(self.packages_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_packages.copy()
        except Exception as e:
            logger.error(f"❌ 加载点数套餐配置失败: {e}")
            return self.default_packages.copy()
    
    def _save_packages(self, packages: List[Dict]) -> bool:
        """保存套餐配置"""
        try:
            self.packages_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.packages_file, 'w', encoding='utf-8') as f:
                json.dump(packages, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ 保存点数套餐配置失败: {e}")
            return False
    
    def _load_orders(self) -> List[Dict]:
        """加载订单记录"""
        try:
            if self.orders_file.exists():
                with open(self.orders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"❌ 加载订单记录失败: {e}")
            return []
    
    def _save_orders(self, orders: List[Dict]) -> bool:
        """保存订单记录"""
        try:
            self.orders_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                json.dump(orders, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ 保存订单记录失败: {e}")
            return False
    
    def get_packages(self, enabled_only: bool = False) -> List[Dict]:
        """获取套餐列表"""
        packages = self._load_packages()
        if enabled_only:
            return [p for p in packages if p.get("enabled", True)]
        return packages
    
    def get_package(self, package_id: str) -> Optional[Dict]:
        """获取单个套餐"""
        packages = self._load_packages()
        for pkg in packages:
            if pkg.get("id") == package_id:
                return pkg
        return None
    
    def add_package(self, package: Dict) -> bool:
        """添加套餐"""
        packages = self._load_packages()
        # 检查ID是否重复
        if any(p.get("id") == package.get("id") for p in packages):
            return False
        packages.append(package)
        return self._save_packages(packages)
    
    def update_package(self, package_id: str, updates: Dict) -> bool:
        """更新套餐"""
        packages = self._load_packages()
        for i, pkg in enumerate(packages):
            if pkg.get("id") == package_id:
                packages[i].update(updates)
                return self._save_packages(packages)
        return False
    
    def delete_package(self, package_id: str) -> bool:
        """删除套餐"""
        packages = self._load_packages()
        packages = [p for p in packages if p.get("id") != package_id]
        return self._save_packages(packages)
    
    def create_order(self, username: str, package_id: str, payment_method: str = "manual") -> Optional[Dict]:
        """创建订单"""
        package = self.get_package(package_id)
        if not package:
            return None
        
        order = {
            "order_id": f"PO{int(time.time() * 1000)}",
            "username": username,
            "package_id": package_id,
            "package_name": package.get("name"),
            "points": package.get("points", 0),
            "bonus": package.get("bonus", 0),
            "total_points": package.get("points", 0) + package.get("bonus", 0),
            "price": package.get("price", 0),
            "currency": package.get("currency", "CNY"),
            "payment_method": payment_method,
            "status": "pending",  # pending, paid, cancelled, completed
            "created_at": time.time(),
            "paid_at": None,
            "completed_at": None
        }
        
        orders = self._load_orders()
        orders.append(order)
        if self._save_orders(orders):
            return order
        return None
    
    def complete_order(self, order_id: str) -> bool:
        """完成订单（支付成功后的处理）"""
        orders = self._load_orders()
        for order in orders:
            if order.get("order_id") == order_id:
                if order.get("status") == "pending":
                    order["status"] = "paid"
                    order["paid_at"] = time.time()
                    # 这里应该调用 auth_manager 来增加用户点数
                    # 为了解耦，我们只标记订单状态，实际点数增加在外部处理
                    if self._save_orders(orders):
                        return True
                break
        return False
    
    def get_user_orders(self, username: str, limit: int = 50) -> List[Dict]:
        """获取用户的订单列表"""
        orders = self._load_orders()
        user_orders = [o for o in orders if o.get("username") == username]
        # 按创建时间倒序排序
        user_orders.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return user_orders[:limit]
    
    def get_all_orders(self, limit: int = 100) -> List[Dict]:
        """获取所有订单（管理员）"""
        orders = self._load_orders()
        orders.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return orders[:limit]
    
    def reset_to_default(self) -> bool:
        """重置为默认套餐"""
        return self._save_packages(self.default_packages.copy())
    
    def update_order_status(self, order_id: str, status: str, **kwargs) -> bool:
        """更新订单状态"""
        orders = self._load_orders()
        for order in orders:
            if order.get("order_id") == order_id:
                order["status"] = status
                order.update(kwargs)
                return self._save_orders(orders)
        return False


# 全局实例
points_package_manager = PointsPackageManager()

