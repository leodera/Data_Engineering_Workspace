import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(override=True)
postgre_url = os.getenv("POSTGRES_URL")
postgre_engine = create_engine(
    postgre_url,
    pool_pre_ping=True
)


query3 = """SELECT 
              c.customer_unique_id,
              COUNT(DISTINCT o.order_id) AS total_orders,
              ROUND(SUM(p.payment_value)::numeric, 2) AS total_spend,
              MAX(o.order_purchase_timestamp::timestamp) AS last_order_date
            FROM olist_ecommerce.orders o
            JOIN olist_ecommerce.customers c ON o.customer_id = c.customer_id
            JOIN olist_ecommerce.order_payments p ON o.order_id = p.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
            ORDER BY total_spend DESC
            LIMIT 15;"""
rfm = pd.read_sql(query3, con = postgre_engine)

