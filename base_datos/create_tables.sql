-- Crear la tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INT NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'comprador'
);

-- Crear la tabla de categorías
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Crear la tabla de productos
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    CONSTRAINT fk_category
        FOREIGN KEY (category_id) 
        REFERENCES categories(id)
        ON DELETE CASCADE
);

-- Crear la tabla del carrito
CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product
        FOREIGN KEY (product_id) 
        REFERENCES products(id)
        ON DELETE CASCADE
);

-- Crear la tabla de órdenes
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_order
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Crear la tabla de items de la orden
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_order
        FOREIGN KEY (order_id) 
        REFERENCES orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product_order
        FOREIGN KEY (product_id) 
        REFERENCES products(id)
        ON DELETE CASCADE
);


INSERT INTO categories (name)
VALUES 
    ('Chocolates'),
    ('Galletas'),
    ('Caramelos'),
    ('Dulces'),
    ('Bebidas'), 
    ('Snacks');


INSERT INTO products (name, description, price, image_path, category_id)
VALUES
    ('Caramelos', 'Dulces de caramelo', 10.0, 'static/uploads/caramelos.jpg', (SELECT id FROM categories WHERE name = 'Dulces')),
    ('Refresco', 'Bebida gaseosa', 15.0, 'static/uploads/refresco.jpg', (SELECT id FROM categories WHERE name = 'Bebidas')),
    ('Chips', 'Papas fritas', 20.0, 'static/uploads/snack.jpg', (SELECT id FROM categories WHERE name = 'Snacks'));
