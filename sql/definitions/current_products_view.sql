CREATE OR REPLACE VIEW product_data AS
WITH
    -- Add vendor column
    add_vendor AS (
        SELECT
            *,
            CASE
                WHEN url LIKE '%metaldesignz%' THEN 'metaldesignz'
                WHEN url LIKE '%theringlord%' THEN 'theringlord'
            END AS vendor
        FROM
            scraped_product_info
    ),
    -- Add constructed sku column that will be unique to each product
    add_constructed_sku AS (
        SELECT
            *,
            CONCAT(
                COALESCE(vendor,        ''), ' | ',
                COALESCE(sku,           ''), ' | ', 
                COALESCE(material,      ''), ' | ', 
                COALESCE(color,         ''), ' | ', 
                COALESCE(rings_per_bag, '')
            ) AS constructed_sku
        FROM
            add_vendor
    ),
    -- Gets the most recent time a product has been scraped
    aggregated_data AS (
        SELECT
            MAX(time_accessed) AS most_recent_scrape_time,
            constructed_sku
        FROM
            add_constructed_sku
        GROUP BY
            constructed_sku
    )
-- Get all of the most recent data
SELECT
    acs.time_accessed,
    acs.vendor,
    acs.sku,
    acs.product_name,
    acs.material,
    acs.color,
    acs.price,
    acs.currency,
    acs.wire_diameter_in,
    acs.wire_diameter_mm,
    acs.wire_diameter_gauge,
    acs.internal_diameter_in,
    acs.internal_diameter_mm,
    acs.aspect_ratio,
    acs.bags_in_stock,
    acs.rings_per_bag,
    acs.url
FROM
    add_constructed_sku AS acs
    LEFT JOIN aggregated_data AS ad ON acs.constructed_sku = ad.constructed_sku
WHERE
    acs.constructed_sku = ad.constructed_sku;
