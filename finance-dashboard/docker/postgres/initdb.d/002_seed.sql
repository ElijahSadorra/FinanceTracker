INSERT INTO categories (name, parent_id, is_system)
VALUES
    ('Uncategorised', NULL, TRUE),
    ('Income', NULL, TRUE),
    ('Groceries', NULL, TRUE),
    ('Utilities', NULL, TRUE),
    ('Transport', NULL, TRUE),
    ('Housing', NULL, TRUE)
ON CONFLICT (name) DO NOTHING;
