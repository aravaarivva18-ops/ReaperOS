#!/usr/bin/env python3
import json
import os
from collections import defaultdict

# Dynamic scratch path calculation
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.getenv("SCRATCH_DIR")
if not SCRATCH_DIR:
    SCRATCH_DIR = os.path.join(project_root, "scratch")

STOCKS_FILE = os.path.join(SCRATCH_DIR, "stocks.json")
ORDERS_FILE = os.path.join(SCRATCH_DIR, "orders.json")
LOGISTIC_REPORT_FILE = os.path.join(SCRATCH_DIR, "logistic_report.json")

# Central warehouses definition
CENTRAL_WAREHOUSES = {
    "коледино", "электросталь", "домодедово", "подольск", "белая дача", 
    "крекшино", "внуково", "пушкино", "обухово", "белые столбы"
}

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def main():
    print("Logistic Sub-agent: Starting inventory and sales analysis...")
    
    stocks_raw = load_json(STOCKS_FILE)
    orders_raw = load_json(ORDERS_FILE)
    
    print(f"Loaded {len(stocks_raw)} stocks records and {len(orders_raw)} orders records.")
    
    # 1. Aggregate daily orders per nmId (last 30 days)
    # orders_raw contains items ordered in the last 30 days.
    nm_orders = defaultdict(list)
    for order in orders_raw:
        nm_id = order.get('nmId')
        # Skip canceled if field exists
        if order.get('isCancel'):
            continue
        nm_orders[nm_id].append(order)
        
    # Calculate daily order velocity
    daily_velocity = {}
    for nm_id, orders in nm_orders.items():
        daily_velocity[nm_id] = len(orders) / 30.0 # 30 days average
        
    # 2. Aggregate stocks per nmId and warehouse
    nm_stocks = defaultdict(int)
    nm_warehouse_stocks = defaultdict(lambda: defaultdict(int))
    
    for stock in stocks_raw:
        nm_id = stock.get('nmId')
        quantity = stock.get('quantity', 0)
        wh_name = stock.get('warehouseName', '').strip()
        
        nm_stocks[nm_id] += quantity
        if wh_name:
            nm_warehouse_stocks[nm_id][wh_name] += quantity
            
    # 3. Analyze each product (nmID)
    results = {}
    
    # Get all unique nmIds from stocks and orders
    all_nm_ids = set(nm_stocks.keys()).union(set(daily_velocity.keys()))
    
    total_central_stock = 0
    total_regional_stock = 0
    
    for nm_id in all_nm_ids:
        stock = nm_stocks.get(nm_id, 0)
        velocity = daily_velocity.get(nm_id, 0.0)
        whs = nm_warehouse_stocks.get(nm_id, {})
        
        # Localization calculations
        central_stock = 0
        regional_stock = 0
        
        wh_details = []
        for wh, q in whs.items():
            wh_details.append({"warehouse": wh, "quantity": q})
            if wh.lower() in CENTRAL_WAREHOUSES:
                central_stock += q
            else:
                regional_stock += q
                
        total_central_stock += central_stock
        total_regional_stock += regional_stock
        
        # Calculate days left
        days_left = 9999
        if velocity > 0:
            days_left = stock / velocity
            
        # Status assignment
        status = "OK"
        warning = ""
        lost_revenue_monthly = 0.0
        
        # Estimate average price from orders
        orders = nm_orders.get(nm_id, [])
        avg_price = 0.0
        if orders:
            prices = [o.get('priceWithDisc', 0.0) for o in orders if o.get('priceWithDisc')]
            if prices:
                avg_price = sum(prices) / len(prices)
                
        if stock == 0 and velocity > 0:
            status = "OUT_OF_STOCK"
            warning = "Товар закончился, продажи идут в ноль (Потеря позиций)"
            lost_revenue_monthly = velocity * 30 * avg_price
        elif days_left <= 3 and velocity > 0:
            status = "CRITICAL_LOW"
            warning = f"Критический остаток на {days_left:.1f} дней. Срочно отгрузить!"
            lost_revenue_monthly = max(0.0, (30 - days_left) * velocity * avg_price)
        elif days_left > 120 and stock > 50:
            status = "OVERSTOCK"
            warning = f"Замороженный неликвид: остаток на {days_left:.0f} дней"
        elif stock > 0 and velocity == 0:
            status = "NO_SALES"
            warning = "Товар лежит на складе, но нет заказов за 30 дней"
            
        results[str(nm_id)] = {
            "nmID": nm_id,
            "total_stock": stock,
            "daily_velocity": round(velocity, 3),
            "days_left": round(days_left, 1) if days_left != 9999 else "N/A",
            "status": status,
            "warning": warning,
            "lost_revenue_monthly": round(lost_revenue_monthly, 2),
            "central_stock": central_stock,
            "regional_stock": regional_stock,
            "localization_index": round((regional_stock / stock * 100), 2) if stock > 0 else 0.0,
            "warehouses": wh_details,
            "avg_price": round(avg_price, 2)
        }
        
    # Overall localization index
    overall_stock = total_central_stock + total_regional_stock
    overall_localization_index = round((total_regional_stock / overall_stock * 100), 2) if overall_stock > 0 else 0.0
    
    report = {
        "overall": {
            "total_central_stock": total_central_stock,
            "total_regional_stock": total_regional_stock,
            "overall_localization_index": overall_localization_index
        },
        "items": results
    }
    
    with open(LOGISTIC_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"Logistic Sub-agent: Completed analysis for {len(results)} items. Saved report to {LOGISTIC_REPORT_FILE}")

if __name__ == "__main__":
    main()
