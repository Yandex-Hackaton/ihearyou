-- Создание пользователя и базы данных
-- (этот файл выполняется автоматически при первом запуске PostgreSQL)
-- Пользователь и пароль уже созданы через переменные окружения PostgreSQL

-- Даем права на базу данных
GRANT ALL PRIVILEGES ON DATABASE ihearyou TO ihearyou_user;

-- Подключаемся к базе данных и даем права на схему
\c ihearyou;

-- Даем права на схему public
GRANT ALL ON SCHEMA public TO ihearyou_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ihearyou_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ihearyou_user;

-- Даем права на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ihearyou_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ihearyou_user;

-- Создание таблиц
CREATE TABLE IF NOT EXISTS users_roles (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS buttons_categories (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    for_user_role_id INTEGER REFERENCES users_roles(id)
);

CREATE TABLE IF NOT EXISTS buttons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,  -- Убрали UNIQUE
    description TEXT,
    content TEXT,
    category_id INTEGER REFERENCES buttons_categories(id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    surname VARCHAR(255),
    patronymic VARCHAR(255),
    birth_date DATE,
    role_id INTEGER REFERENCES users_roles(id)
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_buttons_title ON buttons(title);
CREATE INDEX IF NOT EXISTS idx_buttons_category_id ON buttons(category_id);  -- Добавили индекс для category_id
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);

-- Вставка ролей пользователей
INSERT INTO users_roles (slug, title, description) VALUES
('parent', 'Родитель', 'Родитель ребенка с нарушением слуха'),
('adult', 'Взрослый', 'Взрослый с нарушением слуха')
ON CONFLICT (slug) DO NOTHING;

-- Вставка категорий кнопок
INSERT INTO buttons_categories (slug, title, description, for_user_role_id) VALUES
('child_concerns', 'Я волнуюсь о слухе ребенка', 'Категория для родителей детей с нарушением слуха', 
 (SELECT id FROM users_roles WHERE slug = 'parent')),
('adult_concerns', 'Я волнуюсь о своем слухе', 'Категория для взрослых с нарушением слуха', 
 (SELECT id FROM users_roles WHERE slug = 'adult'))
ON CONFLICT (slug) DO NOTHING;

-- Вставка кнопок для категории "Я волнуюсь о слухе ребенка"
INSERT INTO buttons (title, description, content, category_id) VALUES
('Диагноз: что делать?', 'Первые шаги, шок, принятие', 'Информация о том, что делать после постановки диагноза', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns')),
('Слуховые аппараты и кохлеарные импланты', 'Технические вопросы, компенсации', 'Информация о слуховых аппаратах и кохлеарных имплантах', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns')),
('Обучение, развитие и социализация', 'Развитие ребенка с нарушением слуха', 'Информация об обучении и развитии ребенка', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns')),
('Инклюзия в детском саду и школе', 'Включение в образовательный процесс', 'Информация об инклюзивном образовании', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns')),
('Поддержка для родителей', 'Психолог, группы, истории', 'Информация о поддержке для родителей', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns')),
('Задать свой вопрос', 'Если не нашли ответа', 'Возможность задать индивидуальный вопрос', 
 (SELECT id FROM buttons_categories WHERE slug = 'child_concerns'));

-- Вставка кнопок для категории "Я волнуюсь о своем слухе"
INSERT INTO buttons (title, description, content, category_id) VALUES
('Диагноз: что делать?', 'Первые шаги, шок, принятие', 'Информация о том, что делать после постановки диагноза', 
 (SELECT id FROM buttons_categories WHERE slug = 'adult_concerns')),
('Слуховые аппараты и кохлеарные импланты', 'Технические вопросы, компенсации', 'Информация о слуховых аппаратах и кохлеарных имплантах', 
 (SELECT id FROM buttons_categories WHERE slug = 'adult_concerns')),
('Поддержка', 'Психологическая и социальная поддержка', 'Информация о поддержке для взрослых', 
 (SELECT id FROM buttons_categories WHERE slug = 'adult_concerns')),
('Задать свой вопрос', 'Если не нашли ответа', 'Возможность задать индивидуальный вопрос', 
 (SELECT id FROM buttons_categories WHERE slug = 'adult_concerns'));