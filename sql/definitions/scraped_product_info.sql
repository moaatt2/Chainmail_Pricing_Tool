CREATE TABLE IF NOT EXISTS scraped_product_info (
    time_accessed        TIMESTAMP,
    url                  VARCHAR(255),
    sku                  VARCHAR(255),
    product_name         VARCHAR(255),
    material             VARCHAR(255),
    price                FLOAT,
    currency             VARCHAR(5),
    wire_diameter_in     FLOAT,
    wire_diameter_mm     FLOAT,
    wire_diameter_gauge  FLOAT,
    internal_diameter_in FLOAT,
    internal_diameter_mm FLOAT,
    aspect_ratio         FLOAT,
    color                VARCHAR(255),
    bags_in_stock        INT,
    rings_per_bag        INT
);