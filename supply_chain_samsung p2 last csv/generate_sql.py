"""Genere supply_chain.sql : CREATE TABLE + INSERT depuis les CSV (sans les *_original)."""
import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "supply_chain.sql")
BATCH = 200  # lignes par INSERT

# types: int = integer, num = numeric, str = text, date = date
TABLES = [
    ("dim_customer", "dim_customer.csv", [
        ("customer_id", "int"), ("customer_key", "str"), ("customer_name", "str"),
        ("country", "str"), ("channel_type", "str"), ("size", "str"),
        ("annual_volume_usd", "int")]),
    ("dim_date", "dim_date.csv", [
        ("date_key", "int"), ("date", "date"), ("year", "int"), ("quarter", "int"),
        ("month", "int"), ("month_name", "str"), ("week", "int"), ("day", "int"),
        ("day_of_week", "int"), ("day_name", "str"), ("is_weekend", "int")]),
    ("dim_facility", "dim_facility.csv", [
        ("facility_id", "int"), ("facility_key", "str"), ("facility_name", "str"),
        ("country", "str"), ("city", "str"), ("facility_type", "str"),
        ("specialization", "str"), ("annual_capacity", "int")]),
    ("dim_product", "dim_product.csv", [
        ("product_id", "int"), ("product_key", "str"), ("product_name", "str"),
        ("category", "str"), ("product_line", "str"), ("spec", "str"),
        ("color", "str"), ("unit_price", "num"), ("unit_cost", "num"),
        ("weight_kg", "num"), ("img", "str")]),
    ("dim_supplier", "dim_supplier.csv", [
        ("supplier_id", "int"), ("supplier_key", "str"), ("supplier_name", "str"),
        ("country", "str"), ("city", "str"), ("specialty", "str"),
        ("tier", "str"), ("avg_quality_score", "num")]),
    ("fact_inventory", "fact_inventory.csv", [
        ("inventory_id", "int"), ("date_key", "int"), ("product_id", "int"),
        ("facility_id", "int"), ("stock_level", "int"),
        ("safety_stock_level", "int"), ("reorder_point", "int")]),
    ("fact_procurement", "fact_procurement.csv", [
        ("procurement_id", "int"), ("order_date_key", "int"), ("product_id", "int"),
        ("supplier_id", "int"), ("order_quantity", "int"), ("unit_cost", "num"),
        ("total_cost", "num"), ("lead_time_days", "int"),
        ("delivery_date_key", "int"), ("quality_score", "num"),
        ("po_number", "str")]),
    ("fact_production", "fact_production.csv", [
        ("production_id", "int"), ("date_key", "int"), ("product_id", "int"),
        ("facility_id", "int"), ("quantity_produced", "int"),
        ("defective_units", "int"), ("defect_rate_pct", "num"),
        ("batch_number", "str")]),
    ("fact_sales", "fact_sales.csv", [
        ("sales_id", "int"), ("date_key", "int"), ("product_id", "int"),
        ("customer_id", "int"), ("quantity_sold", "int"), ("unit_price", "num"),
        ("discount_pct", "num"), ("discount_amount", "num"),
        ("gross_revenue", "num"), ("net_revenue", "num"), ("total_cost", "num"),
        ("profit", "num"), ("profit_margin_pct", "num"), ("order_number", "str")]),
    ("fact_shipment", "fact_shipment.csv", [
        ("shipment_id", "int"), ("ship_date_key", "int"),
        ("delivery_date_key", "int"), ("product_id", "int"),
        ("facility_id", "int"), ("customer_id", "int"), ("quantity", "int"),
        ("carrier", "str"), ("status", "str"), ("shipping_cost", "num"),
        ("total_weight_kg", "num"), ("tracking_number", "str"),
        ("delay_reason", "str")]),
]

DDL = """-- Supply chain schema - generated from CSV files
BEGIN;

DROP TABLE IF EXISTS fact_shipment, fact_sales, fact_production, fact_procurement, fact_inventory CASCADE;
DROP TABLE IF EXISTS dim_customer, dim_date, dim_facility, dim_product, dim_supplier CASCADE;

CREATE TABLE dim_customer (
    customer_id        INTEGER PRIMARY KEY,
    customer_key       VARCHAR(20)  NOT NULL UNIQUE,
    customer_name      VARCHAR(100) NOT NULL,
    country            VARCHAR(50)  NOT NULL,
    channel_type       VARCHAR(20)  NOT NULL,
    size               VARCHAR(20),
    annual_volume_usd  BIGINT
);

CREATE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,
    date         DATE        NOT NULL,
    year         INTEGER     NOT NULL,
    quarter      SMALLINT    NOT NULL,
    month        SMALLINT    NOT NULL,
    month_name   VARCHAR(15) NOT NULL,
    week         SMALLINT,
    day          SMALLINT    NOT NULL,
    day_of_week  SMALLINT,
    day_name     VARCHAR(15),
    is_weekend   SMALLINT
);

CREATE TABLE dim_facility (
    facility_id      INTEGER PRIMARY KEY,
    facility_key     VARCHAR(20)  NOT NULL UNIQUE,
    facility_name    VARCHAR(100) NOT NULL,
    country          VARCHAR(50)  NOT NULL,
    city             VARCHAR(50),
    facility_type    VARCHAR(30)  NOT NULL,
    specialization   VARCHAR(50),
    annual_capacity  INTEGER
);

CREATE TABLE dim_product (
    product_id    INTEGER PRIMARY KEY,
    product_key   VARCHAR(30)  NOT NULL UNIQUE,
    product_name  VARCHAR(100) NOT NULL,
    category      VARCHAR(30)  NOT NULL,
    product_line  VARCHAR(30),
    spec          VARCHAR(30),
    color         VARCHAR(30),
    unit_price    NUMERIC(10,2),
    unit_cost     NUMERIC(10,2),
    weight_kg     NUMERIC(6,2),
    img           VARCHAR(255)
);

CREATE TABLE dim_supplier (
    supplier_id        INTEGER PRIMARY KEY,
    supplier_key       VARCHAR(20)  NOT NULL UNIQUE,
    supplier_name      VARCHAR(100) NOT NULL,
    country            VARCHAR(50)  NOT NULL,
    city               VARCHAR(50),
    specialty          VARCHAR(60),
    tier               VARCHAR(10),
    avg_quality_score  NUMERIC(4,1)
);

CREATE TABLE fact_inventory (
    inventory_id        INTEGER PRIMARY KEY,
    date_key            INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_id          INTEGER NOT NULL REFERENCES dim_product(product_id),
    facility_id         INTEGER NOT NULL REFERENCES dim_facility(facility_id),
    stock_level         INTEGER,
    safety_stock_level  INTEGER,
    reorder_point       INTEGER
);

CREATE TABLE fact_procurement (
    procurement_id      INTEGER PRIMARY KEY,
    order_date_key      INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_id          INTEGER NOT NULL REFERENCES dim_product(product_id),
    supplier_id         INTEGER NOT NULL REFERENCES dim_supplier(supplier_id),
    order_quantity      INTEGER,
    unit_cost           NUMERIC(12,2),
    total_cost          NUMERIC(14,2),
    lead_time_days      INTEGER,
    delivery_date_key   INTEGER REFERENCES dim_date(date_key),
    quality_score       NUMERIC(4,1),
    po_number           VARCHAR(20)
);

CREATE TABLE fact_production (
    production_id      INTEGER PRIMARY KEY,
    date_key           INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_id         INTEGER NOT NULL REFERENCES dim_product(product_id),
    facility_id        INTEGER NOT NULL REFERENCES dim_facility(facility_id),
    quantity_produced  INTEGER,
    defective_units    INTEGER,
    defect_rate_pct    NUMERIC(5,2),
    batch_number       VARCHAR(20)
);

CREATE TABLE fact_sales (
    sales_id            INTEGER PRIMARY KEY,
    date_key            INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_id          INTEGER NOT NULL REFERENCES dim_product(product_id),
    customer_id         INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    quantity_sold       INTEGER,
    unit_price          NUMERIC(10,2),
    discount_pct        SMALLINT,
    discount_amount     NUMERIC(14,2),
    gross_revenue       NUMERIC(14,2),
    net_revenue         NUMERIC(14,2),
    total_cost          NUMERIC(14,2),
    profit              NUMERIC(14,2),
    profit_margin_pct   NUMERIC(6,2),
    order_number        VARCHAR(20)
);

CREATE TABLE fact_shipment (
    shipment_id        INTEGER PRIMARY KEY,
    ship_date_key      INTEGER NOT NULL REFERENCES dim_date(date_key),
    delivery_date_key  INTEGER REFERENCES dim_date(date_key),
    product_id         INTEGER NOT NULL REFERENCES dim_product(product_id),
    facility_id        INTEGER NOT NULL REFERENCES dim_facility(facility_id),
    customer_id        INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    quantity           INTEGER,
    carrier            VARCHAR(30),
    status             VARCHAR(20),
    shipping_cost      NUMERIC(10,2),
    total_weight_kg    NUMERIC(12,2),
    tracking_number    VARCHAR(20),
    delay_reason       VARCHAR(60)
);
"""


def lit(value, typ):
    value = value.strip()
    if value == "":
        return "NULL"
    if typ in ("int", "num"):
        return value
    return "'" + value.replace("'", "''") + "'"


with open(OUT, "w", encoding="utf-8") as out:
    out.write(DDL)
    for table, csvfile, cols in TABLES:
        path = os.path.join(BASE, csvfile)
        colnames = ", ".join(c[0] for c in cols)
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            expected = [c[0] for c in cols]
            if [h.lower() for h in header] != expected:
                print(f"WARN header {csvfile}: {header}")
            batch, count = [], 0
            for row in reader:
                if not row or all(not v.strip() for v in row):
                    continue
                batch.append("(" + ",".join(
                    lit(v, cols[i][1]) for i, v in enumerate(row[:len(cols)])) + ")")
                count += 1
                if len(batch) >= BATCH:
                    out.write(f"\nINSERT INTO {table} ({colnames}) VALUES\n")
                    out.write(",\n".join(batch) + ";\n")
                    batch = []
            if batch:
                out.write(f"\nINSERT INTO {table} ({colnames}) VALUES\n")
                out.write(",\n".join(batch) + ";\n")
            print(f"{table}: {count} lignes")
    out.write("\nCOMMIT;\n")

print("OK ->", OUT)
