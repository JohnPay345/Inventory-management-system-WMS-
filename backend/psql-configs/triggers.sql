-- 1. Создаем универсальную функцию логирования
CREATE OR REPLACE FUNCTION process_warehouse_audit()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id UUID;
    v_ip_address VARCHAR(45);
    v_old_json JSONB := NULL;
    v_new_json JSONB := NULL;
    v_pk_column_name TEXT;
    v_entity_id UUID;
BEGIN
    -- Считываем имя колонки первичного ключа из аргумента триггера
    v_pk_column_name := TG_ARGV[0];

    -- Безопасно извлекаем переменные контекста сессии
    -- TODO: Понять, как брать user_id для логов
    BEGIN v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::UUID; EXCEPTION WHEN OTHERS THEN v_user_id := NULL; END;
    BEGIN v_ip_address := NULLIF(current_setting('app.current_ip_address', true), ''); EXCEPTION WHEN OTHERS THEN v_ip_address := NULL; END;

    -- Наполняем JSONB в зависимости от типа операции
    IF (TG_OP = 'INSERT') THEN
        v_new_json := ROW_TO_JSON(NEW)::JSONB;
        v_entity_id := (v_new_json ->> v_pk_column_name)::UUID;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old_json := ROW_TO_JSON(OLD)::JSONB;
        v_new_json := ROW_TO_JSON(NEW)::JSONB;
        v_entity_id := (v_new_json ->> v_pk_column_name)::UUID;
    ELSIF (TG_OP = 'DELETE') THEN
        v_old_json := ROW_TO_JSON(OLD)::JSONB;
        v_entity_id := (v_old_json ->> v_pk_column_name)::UUID;
    END IF;

    -- Записываем строку аудита в вашу таблицу
    INSERT INTO warehouse_audit_log (
        log_id,
        user_id,
        entity_name,
        entity_id,
        action_type,
        old_values,
        new_values,
        ip_address,
        created_at
    )
    VALUES (
        uuidv7(),                           -- Генерация UUID для лога
        v_user_id,                         -- ID пользователя из FastAPI
        TG_TABLE_NAME,                     -- Имя таблицы, где было изменение
        v_entity_id,                       -- Выделенный UUID сущности
        lower(TG_OP)::action_type_log,            -- Тип операции (INSERT, UPDATE, DELETE) кастуем в ваш ENUM
        v_old_json,                        -- Состояние ДО
        v_new_json,                        -- Состояние ПОСЛЕ
        v_ip_address,                      -- IP-адрес из FastAPI
        CURRENT_TIMESTAMP
    );

    -- Возвращаем результат для корректного завершения операции
    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- 2. Привязываем триггеры к таблицам с указанием их первичных ключей

-- Для таблицы Products
DROP TRIGGER IF EXISTS trg_audit_products ON products;
CREATE TRIGGER trg_audit_products
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('product_id');

-- Для таблицы WarehouseCell
DROP TRIGGER IF EXISTS trg_audit_warehouse_cells ON warehouse_cells;
CREATE TRIGGER trg_audit_warehouse_cells
AFTER INSERT OR UPDATE OR DELETE ON warehouse_cells
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('warehouse_cell_id');

-- Для таблицы Users
DROP TRIGGER IF EXISTS trg_audit_users ON users;
CREATE TRIGGER trg_audit_users
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('user_id');

-- Для таблицы InboundInvoice
DROP TRIGGER IF EXISTS trg_audit_inbound_invoices ON inbound_invoices;
CREATE TRIGGER trg_audit_inbound_invoices
AFTER INSERT OR UPDATE OR DELETE ON inbound_invoices
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('inbound_invoice_id');

-- Для таблицы InboundInvoiceItem
DROP TRIGGER IF EXISTS trg_audit_inbound_invoice_items ON inbound_invoice_items;
CREATE TRIGGER trg_audit_inbound_invoice_items
AFTER INSERT OR UPDATE OR DELETE ON inbound_invoice_items
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('inbound_invoice_item_id');

-- Для таблицы InventoryStocks (составной ключ, отслеживаем по product_id)
DROP TRIGGER IF EXISTS trg_audit_inventory_stocks ON inventory_stocks;
CREATE TRIGGER trg_audit_inventory_stocks
AFTER INSERT OR UPDATE OR DELETE ON inventory_stocks
FOR EACH ROW EXECUTE FUNCTION process_warehouse_audit('product_id');
