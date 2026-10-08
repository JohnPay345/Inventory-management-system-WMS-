DO $$
DECLARE
    -- Переменные для хранения динамических UUID
    v_user_manager UUID := gen_random_uuid();
    v_user_sk      UUID := gen_random_uuid();
    v_user_picker  UUID := gen_random_uuid();
    
    v_prod_iphone  UUID := gen_random_uuid();
    v_prod_samsung UUID := gen_random_uuid();
    
    v_cell_a1      UUID := gen_random_uuid();
    v_cell_a2      UUID := gen_random_uuid();
    
    v_invoice_1    UUID := gen_random_uuid();
BEGIN
    -- 1. НАПОЛНЕНИЕ ТАБЛИЦЫ ПОЛЬЗОВАТЕЛЕЙ (users)
    INSERT INTO users (user_id, first_name, middle_name, last_name, username, password_hash, role, is_active, created_at)
    VALUES 
      (v_user_manager, 'Алексей', 'Петрович', 'Иванов', 'manager_alex', '$2b$12$4mDKD/CyA25CBwlaAc5KU4VUZZmcbJTCXBYdZxtIE6OyQPdoDfqjE', 'manager', true, now()),
      (v_user_sk, 'Дмитрий', 'Сергеевич', 'Петров', 'sk_dmitry', '$2b$12$DfSx1PaJBK9t0kSjCdYTAnkA6dQOL7TLdFiYmmmXcjfdUP/FhTTGU', 'storekeeper', true, now()),
      (v_user_picker, 'Ольга', 'Николаевна', 'Сидорова', 'picker_olga', '$2b$12$l/.AQ92hBkoNkWjCUZilcR2kItFjrhORH7hmKarzUopWLkd/d.SDB', 'picker', true, now())
    ON CONFLICT (username) DO NOTHING;

    -- 2. НАПОЛНЕНИЕ ТАБЛИЦЫ ТОВАРОВ (products)
    INSERT INTO products (product_id, sku, barcode, title, description, current_price, weight_kg, is_active, created_at)
    VALUES 
      (v_prod_iphone, 'SKU-IPHONE15', '4601234567890', 'Смартфон Apple iPhone 15', '128GB, Черный', 89990.00, 0.17, true, now()),
      (v_prod_samsung, 'SKU-SAMS24', '4601234567891', 'Смартфон Samsung Galaxy S24', '256GB, Серый', 79990.00, 0.16, true, now())
    ON CONFLICT (sku) DO NOTHING;

    -- 3. НАПОЛНЕНИЕ ТАБЛИЦЫ ЯЧЕЕК СКЛАДА (warehouse_cells)
    INSERT INTO warehouse_cells (warehouse_cell_id, zone_code, rack_number, shelf_number, max_weight_kg, current_weight_kg, is_occupied)
    VALUES 
      (v_cell_a1, 'A-01', 1, 1, 100.00, 0.00, false),
      (v_cell_a2, 'A-02', 1, 2, 100.00, 0.00, false)
    ON CONFLICT (zone_code) DO NOTHING;

    -- 4. НАПОЛНЕНИЕ ТАБЛИЦЫ ОСТАТКОВ (inventory_stocks)
    -- Пытаемся получить UUID, если записи уже существовали из-за ON CONFLICT выше
    SELECT COALESCE((SELECT product_id FROM products WHERE sku = 'SKU-IPHONE15'), v_prod_iphone) INTO v_prod_iphone;
    SELECT COALESCE((SELECT warehouse_cell_id FROM warehouse_cells WHERE zone_code = 'A-01'), v_cell_a1) INTO v_cell_a1;
    SELECT COALESCE((SELECT product_id FROM products WHERE sku = 'SKU-SAMS24'), v_prod_samsung) INTO v_prod_samsung;
    SELECT COALESCE((SELECT warehouse_cell_id FROM warehouse_cells WHERE zone_code = 'A-02'), v_cell_a2) INTO v_cell_a2;
    SELECT COALESCE((SELECT user_id FROM users WHERE username = 'manager_alex'), v_user_manager) INTO v_user_manager;

    INSERT INTO inventory_stocks (product_id, cell_id, quantity)
    VALUES 
      (v_prod_iphone, v_cell_a1, 10),
      (v_prod_samsung, v_cell_a2, 5)
    ON CONFLICT (product_id, cell_id) DO NOTHING;

    -- 5. НАКЛАДНЫЕ ПОСТАВКИ (inbound_invoices)
    INSERT INTO inbound_invoices (inbound_invoice_id, invoice_number, supplier_name, status, received_at, created_by, created_at, updated_at)
    VALUES 
      (v_invoice_1, 'INV-2026-001', 'ООО ТехноОпт', 'posted', now(), v_user_manager, now(), now())
    ON CONFLICT (invoice_number) DO NOTHING;

    -- 6. ПОЗИЦИИ В НАКЛАДНЫХ (inbound_invoice_items)
    SELECT COALESCE((SELECT inbound_invoice_id FROM inbound_invoices WHERE invoice_number = 'INV-2026-001'), v_invoice_1) INTO v_invoice_1;

    INSERT INTO inbound_invoice_items (inbound_invoice_item_id, invoice_id, product_id, target_cell_id, quantity, price_at_received)
    VALUES 
      (gen_random_uuid(), v_invoice_1, v_prod_iphone, v_cell_a1, 10, 85000.00),
      (gen_random_uuid(), v_invoice_1, v_prod_samsung, v_cell_a2, 5, 72000.00);
END $$;
