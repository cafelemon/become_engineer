DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    sold_at TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0)
);

CREATE INDEX idx_sales_sold_at ON sales(sold_at);
CREATE INDEX idx_sales_product_name ON sales(product_name);

INSERT INTO sales (sold_at, product_name, quantity, unit_price_cents) VALUES
    ('2025-01-05', 'Keyboard', 2, 29900),
    ('2025-01-12', 'Mouse', 3, 9900),
    ('2025-01-20', 'Keyboard', 1, 29900),
    ('2025-02-03', 'Monitor', 2, 129900),
    ('2025-02-18', 'Keyboard', 4, 28900),
    ('2025-03-02', 'Mouse', 5, 9500);
