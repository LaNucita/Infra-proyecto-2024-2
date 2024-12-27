# libreria principal
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response

# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# librerias productos
from datetime import datetime
import os
# librerias de chat
from flask_socketio import SocketIO, emit

#peticiones api
import requests

app = Flask(__name__)
app.secret_key = '21852130947293875902837958237f'
# # Configuración de PostgreSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://administrador:admin@localhost:5432/Dulceria'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# Configuración de Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'  # Redirige a esta vista si no está autenticado
# login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
# login_manager.login_message_category = "warning"

#socket para interacion cliente vendedor
socketio = SocketIO(app)

# Lista de usuarios conectados (aquí podrías implementar un sistema real de usuarios)
users = {}

api_url = os.getenv('API_URL', 'http://127.0.0.1:8080')
fotos_url = api_url + "/api/get_image/"
# app.config['fotos_url'] = api_url + "/api/get_image/"


    
@app.route('/register', methods=['GET', 'POST'])
def register():
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado

    if user_id:  # Si ya está autenticado, redirige al dashboard
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        username = request.form['username']
        password = request.form['password']
        
        # URL de la API (ajustar según corresponda)
        url = api_url + "/api/register"
        # Realizamos la solicitud POST al backend con las credenciales
        response = requests.post(url, data=request.form)
        data = response.json()
        mensaje = data.get("message","")
        if response.status_code == 200:
            flash('Usuario Creado Correctamente.', 'success')
            render_template('login.html')
        else:
            flash(f'Error: {mensaje}', 'danger')
            render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado

    if user_id:  # Si ya está autenticado, redirige al dashboard
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # URL de la API (ajustar según corresponda)
        url = api_url + "/api/login"

        # Realizamos la solicitud POST al backend con las credenciales
        response = requests.post(url, data=request.form)

        if response.status_code == 200:
            data = response.json()
            user_data = data.get("user_data",[])
            # Si la respuesta es exitosa, obtenemos los datos del usuario
            # Guardamos la ID del usuario en la cookie
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('user_id', str(user_data['user_id']), max_age=3600)  # 1 hora de expiración
            # Aquí se gestionaría la sesión del usuario (por ejemplo, usando Flask-Login)
            # Podrías almacenar los datos en la sesión o hacer algo similar
            flash('Inicio de sesión exitoso.', 'success')
            return resp
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')




@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Obtener la información del carrito y pedidos desde el backend y renderizar la plantilla."""
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado
    if not user_id:
        flash('No estás autenticado.', 'danger')
        return redirect(url_for('login'))
    # URL de la API con el user_id
    url = api_url + f"/api/dashboard?user_id={user_id}"

    # Realizar solicitud GET al backend para obtener el carrito y pedidos
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        cart_items = data.get('cart_items', [])
        cart_total = data.get('cart_total', 0)
        orders = data.get('orders', [])
        user_data = data.get('user_data', [])
    else:
        cart_items = []
        cart_total = 0
        orders = []
        user_data = []

    # Renderizar la plantilla con la información del carrito y pedidos
    return render_template('dashboard.html', cart_items=cart_items, cart_total=cart_total, orders=orders, user_data=user_data, fotos_url= fotos_url)


#cerrar session
@app.route('/logout')
def logout():
    # Eliminar la cookie de la ID del usuario
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('user_id')  # Elimina la cookie 'user_id'

    flash('Has cerrado sesión.', 'info')
    return resp

# ============================== fin de incio de session ====================================


@app.route('/')
def index():
    # URL de la API (asegúrate de que api_url esté configurado correctamente)
    url = api_url  # Cambia esta URL si el backend está en otro servidor

    # Realizamos la solicitud GET a la API
    response = requests.get(f"{url}/api/get_products")
    
    # Convertimos la respuesta JSON en un diccionario de Python
    if response.status_code == 200:  # Verificamos que la solicitud fue exitosa
        data = response.json()
        products = data.get("products", [])
        categories = data.get("categories", [])
        featured_product = products[0] if products else []
    else:
        products = []
        categories = []
        featured_product = []

    # Renderizamos la plantilla con los datos obtenidos
    return render_template('index.html', categories=categories, products=products, featured_product=featured_product, fotos_url=fotos_url)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado
    if not user_id:
        flash('No estás autenticado.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        
        # Enviar los datos al backend
        url = api_url + "/api/add_product"
        response = requests.post(url, data=request.form, files=request.files)

        if response.status_code == 201:
            flash('Producto agregado exitosamente.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error al agregar el producto: ' + response.json().get('error', 'Error desconocido'), 'danger')
            return redirect(url_for('add_product'))

    # Obtener las categorías desde el backend
    url = api_url + f"/api/get_categories"
    response = requests.get(url)

    if response.status_code == 200:
        categories = response.json()
    else:
        flash('Error al obtener categorías.', 'danger')
        categories = []

    return render_template('add_product.html', categories=categories, fotos_url=fotos_url)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Renderiza la página de detalles del producto."""
    # URL de la API
    url = api_url + f"/api/product/{product_id}"

    # Solicitar datos al backend
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        product = data.get('product', {})
        related_products = data.get('related_products', [])
    else:
        flash('Error al obtener los detalles del producto.', 'danger')
        return redirect(url_for('index'))

    # Renderizar la plantilla con los datos
    return render_template('product_detail.html', product=product, related_products=related_products,fotos_url=fotos_url)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Enviar el ID de usuario al backend para agregar un producto al carrito."""
    # Obtener el user_id desde la cookie o la sesión del frontend
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado
    if not user_id:
        flash('No estás autenticado.', 'danger')
        return redirect(url_for('login'))
    # URL de la API
    url = api_url + f"/api/add_to_cart/{product_id}"

    # Realizar solicitud POST al backend con el user_id en el cuerpo de la solicitud
    response = requests.post(url, json={'user_id': user_id})

    if response.status_code == 200:
        data = response.json()
        flash(data.get('message', 'Producto agregado al carrito.'), 'success')
    else:
        data = response.json()
        flash(data.get('message', 'No se pudo agregar el producto al carrito.'), 'danger')

    return redirect(url_for('carrito'))



# ==================== compras ==============================

@app.route('/carrito')
def carrito():
    """Obtener los productos en el carrito desde el backend y renderizar la plantilla."""
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado
    if not user_id:
        flash('No estás autenticado.', 'danger')
        return redirect(url_for('login'))

    # URL de la API
    url = api_url + f"/api/carrito?user_id={user_id}"

    # Realizar solicitud GET al backend para obtener los productos del carrito
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        cart_items = data.get('cart_items', [])
        cart_total = data.get('cart_total', 0)
    else:
        cart_items = []
        cart_total = 0
    print(cart_items, cart_total)

    # Renderizar la plantilla con los productos del carrito y el total
    return render_template('carrito.html', cart_items=cart_items, cart_total=cart_total,fotos_url=fotos_url)

@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    """Eliminar un producto del carrito y actualizar la vista."""
    # cart_id = request.form['cart_id']
    user_id = request.cookies.get('user_id')  # Obtener el ID del usuario logueado
    if not user_id:
        flash('No estás autenticado.', 'danger')
        return redirect(url_for('login'))

    # URL de la API
    url = api_url + f"/api/remove_from_cart/{cart_id}?user_id={user_id}"

    # Realizar solicitud POST al backend para eliminar el producto del carrito
    response = requests.post(url)

    if response.status_code == 200:
        flash('Producto eliminado del carrito.', 'success')
    else:
        flash('No se pudo eliminar el producto.', 'danger')

    return redirect(url_for('carrito'))


# ======================== sistema envio de mensajes cliente producto ============================
# Ruta para el chat de soporte (cualquier usuario puede actuar como soporte)
@app.route('/soporte')
def soporte():
    return render_template('soporte.html')

# Maneja la conexión de un nuevo cliente (ya sea comprador o soporte)
@socketio.on('connect')
def handle_connect():
    print("Un cliente se ha conectado.")
    emit('response', {'message': '¡Hola! ¿En qué puedo ayudarte hoy?'})
@socketio.on('send_message')
def handle_message(data):
    user = data['user']
    message = data['message']
    role = data['role']  # Recibimos el rol directamente desde el cliente

    # Si el rol es 'soporte', los mensajes se pueden enviar a todos los demás
    if role == 'soporte':
        print(f"Mensaje de Soporte ({user}): {message}")
        emit('response', {'message': f"**Soporte** ({user}): {message}"}, broadcast=True)
    else:
        print(f"Mensaje de Comprador ({user}): {message}")
        emit('response', {'message': f"{user}: {message}"}, broadcast=True)

# Desconexión del cliente
@socketio.on('disconnect')
def handle_disconnect():
    print("Un cliente se ha desconectado.")

# ============================ busqueda ===============================

@app.route('/search', methods=['GET'])
def search_products():
    """Obtener los productos desde el backend según los criterios de búsqueda y renderizar la plantilla."""
    query = request.args.get('query', '')
    category_id = request.args.get('category', None)

    # URL de la API
    url = api_url + f"/api/search?query={query}&category={category_id}"

    # Realizar solicitud GET al backend para obtener los productos
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        categories = data.get('category', [])
    else:
        products = []

    

    # Renderizar la plantilla con los productos y categorías
    return render_template('search.html', products=products, categories=categories,fotos_url=fotos_url)

if __name__ == '__main__':
    #db.create_all()  # Crear tablas si no existen
    app.run(debug=True)
