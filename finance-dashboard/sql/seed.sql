-- 1) Parents / top-level categories
INSERT INTO categories (name, parent_id, is_system)
VALUES
  ('Uncategorised', NULL, TRUE),
  ('Income',         NULL, TRUE),
  ('Food',           NULL, FALSE),
  ('Social life',    NULL, FALSE),
  ('Transportation', NULL, FALSE),
  ('Household',      NULL, FALSE),
  ('Apparel',        NULL, FALSE),
  ('Health',         NULL, FALSE),
  ('Education',      NULL, FALSE),
  ('Gift',           NULL, FALSE),
  ('Tech',           NULL, FALSE),
  ('Gym',            NULL, FALSE),
  ('Insurance',      NULL, FALSE),
  ('Subscription',   NULL, FALSE),
  ('Dog',            NULL, FALSE),
  ('Bills',          NULL, FALSE)
ON CONFLICT (name) DO NOTHING;

-- 2) Subcategories for Food
INSERT INTO categories (name, parent_id, is_system)
VALUES
  ('Eating out', (SELECT id FROM categories WHERE name = 'Food'), FALSE),
  ('Groceries',  (SELECT id FROM categories WHERE name = 'Food'), FALSE)
ON CONFLICT (name) DO NOTHING;

-- 3) Subcategories for Transportation
INSERT INTO categories (name, parent_id, is_system)
VALUES
  ('Train', (SELECT id FROM categories WHERE name = 'Transportation'), FALSE),
  ('Fuel',  (SELECT id FROM categories WHERE name = 'Transportation'), FALSE)
ON CONFLICT (name) DO NOTHING;