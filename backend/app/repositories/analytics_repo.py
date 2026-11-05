from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.user import User
from backend.app.models.catalog import Product
from backend.app.models.order import Order, OrderItem, Payment

class AnalyticsRepository:
    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Calculates real dashboard metrics directly from the database."""
        # 1. Total registered customers
        total_customers = User.query.filter_by(role="customer").count()

        # 2. Total active products
        total_products = Product.query.filter_by(is_active=True).count()

        # 3. Total orders placed
        total_orders = Order.query.count()

        # 4. Total revenue from completed/confirmed orders
        revenue_result = (
            db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
            .filter(Order.status.in_(["confirmed", "processing", "shipped", "delivered"]))
            .first()
        )
        total_revenue = round(float(revenue_result[0]), 2) if revenue_result else 0.0

        # 5. Pending orders
        pending_orders = Order.query.filter_by(status="pending").count()

        # 6. Low stock products
        low_stock_products = (
            Product.query.filter(
                Product.stock <= Product.low_stock_threshold,
                Product.is_active == True,
            )
            .order_by(Product.stock.asc())
            .limit(10)
            .all()
        )
        low_stock_count = Product.query.filter(
            Product.stock <= Product.low_stock_threshold,
            Product.is_active == True,
        ).count()

        # 7. Recent orders (latest 5)
        recent_orders = (
            Order.query.options(
                joinedload(Order.user),
                joinedload(Order.items),
            )
            .order_by(desc(Order.created_at))
            .limit(5)
            .all()
        )

        # 8. Sales time series for the past 14 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)
        daily_sales_raw = (
            db.session.query(
                func.date(Order.created_at).label("order_date"),
                func.coalesce(func.sum(Order.total_amount), 0.0).label("daily_revenue"),
                func.count(Order.id).label("daily_orders"),
            )
            .filter(
                Order.created_at >= cutoff_date,
                Order.status.in_(["confirmed", "processing", "shipped", "delivered"]),
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at).asc())
            .all()
        )

        daily_sales = [
            {
                "date": str(row.order_date),
                "revenue": round(float(row.daily_revenue), 2),
                "orders": int(row.daily_orders),
            }
            for row in daily_sales_raw
        ]

        return {
            "total_customers": total_customers,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "low_stock_count": low_stock_count,
            "low_stock_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "stock": p.stock,
                    "low_stock_threshold": p.low_stock_threshold,
                }
                for p in low_stock_products
            ],
            "recent_orders": [
                {
                    "id": o.id,
                    "order_number": o.order_number,
                    "customer_name": f"{o.user.first_name} {o.user.last_name}" if o.user else "Guest",
                    "status": o.status,
                    "total_amount": float(o.total_amount),
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                }
                for o in recent_orders
            ],
            "sales_time_series": daily_sales,
        }
