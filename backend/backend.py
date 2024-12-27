from flask import Flask, request, jsonify,send_from_directory
# from models import db, Product, Category
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
# librerias productos
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os
# login
from werkzeug.security import generate_password_hash, check_password_hash
# Ruta para obtener los productos
app = Flask(__name__)

#configuracoines
app.secret_key = '21852130947293875902837958237f'
# Configuración de PostgreSQL

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','postgresql://administrador:admin@postgres:5432/Dulceria')

print(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# modelos

# Modelo de usuario
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)  # Nombre
    last_name = db.Column(db.String(50), nullable=False)   # Apellido
    age = db.Column(db.Integer, nullable=False)           # Edad
    username = db.Column(db.String(50), unique=True, nullable=False)  # Nombre de usuario
    password_hash = db.Column(db.String(255), nullable=False)  # Contraseña (hash)
    role = db.Column(db.String(20), default='comprador')  # Rol (por defecto, es comprador)
    def get_id(self):
        return str(self.id) 

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relación con productos
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # Ruta de la imagen local
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # Relación con la categoría
    # category = db.relationship('Category', backref='products')  # Relación inversa

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')



# Ruta para obtener los productos y categorías en formato JSON
@app.route('/api/get_products', methods=['GET'])
def get_products():
    # Consultamos los productos y las categorías desde la base de datos
    products = Product.query.all()
    categories = Category.query.all()

    # Convertimos los productos a un formato de lista de diccionarios
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'image_path': product.image_path,
            'category_id': product.category_id
        })

    # Convertimos las categorías a un formato de lista de diccionarios
    categories_data = []
    for category in categories:
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'image_path': product.image_path
                }
                for product in category.products
            ]
        })

    # Devolvemos los datos como JSON
    return jsonify({
        'products': products_data,
        'categories': categories_data
    })
    

@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    """API para agregar un producto."""
    try:
        # Obtener los datos del formulario
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']
        category_id = request.form['category_id']

        # Guardar la imagen en el sistema de archivos
        # filename = secure_filename(image.filename)
        unique_filename = str(uuid.uuid4()) + secure_filename(image.filename)

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image.save(image_path)

        # Guardar el producto en la base de datos
        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            image_path=unique_filename,
            category_id=category_id
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'message': 'Producto agregado exitosamente.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/get_categories', methods=['GET'])
def api_get_categories():
    """API para obtener todas las categorías."""
    categories = Category.query.all()
    categories_data = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(categories_data), 200

@app.route('/api/product/<int:product_id>', methods=['GET'])
def api_product_detail(product_id):
    """API para obtener detalles de un producto y productos relacionados."""
    product = Product.query.get_or_404(product_id)

    # Obtener productos relacionados de la misma categoría
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(5).all()

    # Formatear los datos para JSON
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_path': product.image_path,
        'category_id': product.category_id
    }

    related_products_data = [
        {
            'id': rp.id,
            'name': rp.name,
            'description': rp.description,
            'price': rp.price,
            'image_path': rp.image_path
        }
        for rp in related_products
    ]

    return jsonify({'product': product_data, 'related_products': related_products_data}), 200

# carrito

@app.route('/api/add_to_cart/<int:product_id>', methods=['POST'])
def api_add_to_cart(product_id):
    """API para agregar un producto al carrito, con el ID de usuario recibido desde el frontend."""
    user_id = request.json.get('user_id')  # Obtener el user_id de la solicitud

    if not user_id:
        return jsonify({'message': 'Se requiere el ID de usuario.'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'El producto no existe.'}), 404

    # Crear una entrada en el carrito
    cart_item = Cart(user_id=user_id, product_id=product_id)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': f'{product.name} fue agregado al carrito.'}), 200

# carrito y cosas xd
@app.route('/api/carrito', methods=['GET'])
def api_carrito():
    """API para obtener los productos en el carrito del usuario, con el ID de usuario recibido desde el frontend."""
    user_id = request.args.get('user_id')  # Obtener el user_id desde los parámetros de la URL

    if not user_id:
        return jsonify({'message': 'Se requiere el ID de usuario.'}), 400

    # Obtener los productos en el carrito del usuario
    cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(Cart.user_id == user_id).all()

    # Calcular el total del carrito
    cart_total = sum(item.Product.price for item in cart_items)

    # Convertir los datos a formato JSON
    cart_items_data = [{
        'item_id': item.Cart.id,
        'product_id': item.Product.id,
        'name': item.Product.name,
        'price': item.Product.price,
        'image_path': item.Product.image_path
    } for item in cart_items]

    return jsonify({
        'cart_items': cart_items_data,
        'cart_total': cart_total
    })

@app.route('/api/remove_from_cart/<int:cart_id>', methods=['POST'])
def api_remove_from_cart(cart_id):
    """API para eliminar un producto del carrito usando el ID del carrito recibido desde el frontend."""
    user_id = request.args.get('user_id')  # Obtener el user_id desde los parámetros de la URL

    if not user_id:
        return jsonify({'message': 'Se requiere el ID de usuario.'}), 400

    # Verificar que el carrito pertenece al usuario
    cart_item = Cart.query.get(cart_id)
    if not cart_item or cart_item.user_id != int(user_id):
        return jsonify({'message': 'No se pudo eliminar el producto. El carrito no pertenece al usuario.'}), 400

    # Eliminar el producto del carrito
    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Producto eliminado del carrito.'})

@app.route('/api/search', methods=['GET'])
def api_search_products():
    """API para buscar productos por nombre, descripción y categoría."""
    query = request.args.get('query', '')
    category_id = request.args.get('category', None)

    # Construir la consulta
    products_query = Product.query

    if query:
        products_query = products_query.filter(Product.name.ilike(f'%{query}%') | Product.description.ilike(f'%{query}%'))

    if category_id:
        products_query = products_query.filter(Product.category_id == category_id)

    # Obtener los productos que coinciden con los criterios de búsqueda
    products = products_query.all()

    # Obtener las categorías para el filtro
    categories = Category.query.all()

    # Convertir los productos a formato JSON
    products_data = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_path': product.image_path
    } for product in products]

    category_data = [{
        'id': categoria.id,
        'name': categoria.name,
        'products': [{
        'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'image_path': product.image_path
            } for product in categoria.products]
    } for categoria in categories]

    return jsonify({'products': products_data, 'category': category_data})


@app.route('/api/dashboard', methods=['GET', 'POST'])
def api_dashboard():
    """API para obtener el carrito del usuario y procesar pagos, usando el user_id enviado por el frontend."""
    user_id = request.args.get('user_id')  # Obtener el user_id desde los parámetros de la URL
    
    if not user_id:
        return jsonify({'message': 'Se requiere el ID de usuario.'}), 400

    if request.method == 'POST':  # Procesar el pago
        cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(Cart.user_id == user_id).all()
        if not cart_items:
            return jsonify({'message': 'Tu carrito está vacío.'}), 400

        # Calcular total
        total_amount = sum(item.Product.price for item in cart_items)

        # Crear un pedido
        new_order = Order(user_id=user_id, total_amount=total_amount)
        db.session.add(new_order)
        db.session.commit()

        # Guardar los productos en el pedido y vaciar el carrito
        for item in cart_items:
            order_item = OrderItem(order_id=new_order.id, product_id=item.Product.id, quantity=1)
            db.session.add(order_item)
            db.session.delete(item.Cart)

        db.session.commit()

        return jsonify({'message': 'Compra realizada con éxito.'})

    # Obtener carrito
    cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(Cart.user_id == user_id).all()
    cart_total = sum(item.Product.price for item in cart_items)

    # Obtener historial de pedidos
    orders = Order.query.filter_by(user_id=user_id).all()
    order_details = []
    
    for order in orders:
        # Obtener los items del pedido y asegurarnos de que sean objetos
        items = db.session.query(OrderItem, Product).join(Product, OrderItem.product_id == Product.id).filter(OrderItem.order_id == order.id).all()
        
        # Aseguramos que los items estén en el formato correcto
        order_items = [{'product_id': item.Product.id, 'name': item.Product.name, 'price': item.Product.price, 'image_path': item.Product.image_path, 'quality': item.OrderItem.quantity} for item in items]
        
        order_details.append({'order':  {'id': order.id, 'total_amount': order.total_amount, 'created_at': order.created_at}, 'items': order_items})

    # Obtener datos del usuario
    user = User.query.get(user_id)
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'age': user.age,
        'role': user.role,  # Mostrar el rol del usuario
        'username': user.username
    }

    return jsonify({
        'user_data': user_data,  # Agregar datos del usuario
        'cart_items': [{'product_id': item.Product.id,"id": item.Cart.id ,'name': item.Product.name, 'price': item.Product.price, "image_path": item.Product.image_path} for item in cart_items],
        'cart_total': cart_total,
        # 'orders': [{'order_id': order['order'].id, 'total_amount': order['order'].total_amount, 'items': order['items']} for order in order_details]
        'orders': order_details
    })


# inicio de session
@app.route('/api/login', methods=['POST'])
def api_login():
    """API para iniciar sesión con usuario y contraseña."""
    username = request.form['username']
    password = request.form['password']
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Faltan datos de usuario o contraseña.'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):    
        # Retorna los datos necesarios para el frontend
        user_data = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'role': user.role,
            'age': user.age
        }
        
        return jsonify({
            'success': True,
            'message': 'Inicio de sesión exitoso.',
            'user_data': user_data
        })
    
    # Si las credenciales son incorrectas
    return jsonify({
        'success': False,
        'message': 'Nombre de usuario o contraseña incorrectos.'
    }), 401


    
@app.route('/api/register', methods=['POST'])
def api_register():
    """API para registrar un nuevo usuario."""
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    age = request.form['age']
    username = request.form['username']
    password = request.form['password']
    
    # Validar la edad
    if not age.isdigit() or int(age) < 0:
        return jsonify({
            'success': False,
            'message': 'Por favor, ingresa una edad válida.'
        }), 400

    # Verificar si el nombre de usuario ya existe
    if User.query.filter_by(username=username).first():
        return jsonify({
            'success': False,
            'message': 'El nombre de usuario ya existe. Intenta con otro.'
        }), 400

    # Encriptar la contraseña
    hashed_password = generate_password_hash(password)

    # Crear un nuevo usuario
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        age=int(age),
        username=username,
        password_hash=hashed_password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Hubo un error al registrar el usuario. Intenta nuevamente.'
        }), 500


@app.route('/api/get_image/<filename>', methods=['GET'])
def get_image(filename):
    """API para obtener una imagen del servidor."""
    try:
        # Asegúrate de que la ruta de la imagen esté en el directorio de carga
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Verifica si la imagen existe
        if os.path.exists(image_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({'error': 'Imagen no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=8080 ,debug=True)
