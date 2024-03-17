# app.py

import os, re, random, string, hashlib
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from urllib.parse import quote
from flask_migrate import Migrate
#from models import Image, Tag

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'  # Carpeta donde se almacenarán las imágenes/gifs subidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Lista de tags (puedes recuperarlos de tu base de datos u otra fuente)
##tags = ['wallpaper']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

# Database config

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tags.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Establece el contexto de la aplicación Flask
with app.app_context():
    # Crea todas las tablas en la base de datos
    db.create_all()
#db.init_app(app)

class ImageTagAssociation(db.Model):
    __tablename__ = 'image_tag_association'
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    tags = db.relationship('Tag', secondary='image_tag_association', backref='images')
    url = db.Column(db.String(255))  # Nuevo campo para la URL de la imagen
    # hash = db.Column(db.String(64), nullable=False, unique=True)  # Asegúrate de que el hash sea único

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No se encontró ningún archivo', 'error')
        #return redirect(url_for('index'))
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        #return redirect(url_for('index'))
        return redirect(request.url)
    
    if file and allowed_file(file.filename):

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Verificar si ya existe un archivo con el mismo nombre
        existing_image = Image.query.filter_by(filename=file.filename).first()
        if existing_image:
            flash('La imagen ya está subida', 'error')
            return redirect(request.url)


        file.save(file_path)
        # print ("Ruta: ", file_path)

        # Guardar el hash en la base de datos
        image = Image(filename=file.filename)
        #image.hash=file_hash
        db.session.add(image)
        #print (image.filename)
        #print (image.tags)
        db.session.commit()
        
        # print ("El hash es: ", image.hash)

        url = request.form.get('url')  # Obtener la URL de la imagen si se proporciona
        if url:
            image.url=url
        
        # Obtener la entrada de texto del formulario y limpiarla
        tags_input = request.form['tags']
        cleaned_input = re.sub(r'[^a-zA-Z0-9\s]+', ' ', tags_input)
        # Dividir la entrada de texto en tags por espacios
        tags = [tag.strip() for tag in cleaned_input.split()]

        # Verificar si el archivo es una imagen GIF
        if file.filename.endswith('.gif'):
            tags.append('gif')  # Añadir el tag "gif" automáticamente

        # Procesar los tags
        for tag_name in tags:
            # Verificar si el tag ya existe en la base de datos
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                # Crear un nuevo tag si no existe
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()

            # Verificar si ya existe la relación entre la imagen y el tag
            existing_association = ImageTagAssociation.query.filter_by(image_id=image.id, tag_id=tag.id).first()
            if not existing_association:
                # Crear la relación entre la imagen y el nuevo tag
                image_tag = ImageTagAssociation(image_id=image.id, tag_id=tag.id)
                db.session.add(image_tag)
        
        # Guardar todos los cambios en la base de datos al final
        db.session.commit()


        # flash('Archivo subido exitosamente.')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search_by_tag():
    # Obtiene el tag especificado en la URL
    tag_name = request.args.get('tag')

    # Verifica si se proporcionó un tag
    if tag_name:
        # Busca el tag en la base de datos
        tag = Tag.query.filter_by(name=tag_name).first()

        # Si el tag existe, obtén las imágenes asociadas
        if tag:
            images = tag.images
            #file_path = images.tag.image_id.filename
            return render_template('search_results.html', images=images, tags=[tag.name])

    # Si no se proporcionó un tag válido, muestra un mensaje de error
    return render_template('search_results.html', error_message='No se encontraron imágenes para el tag especificado.')

# Definimos la nueva ruta para la búsqueda de múltiples tags
@app.route('/search_by_multiple_tags', methods=['GET'])
def search_by_multiple_tags():
    # Obtener los tags especificados por el usuario desde la URL
    tags_input = request.args.get('tags')

    if tags_input:
        # Separar los tags por espacios
        tags = tags_input.split()
        
        # Realizar la búsqueda en la base de datos para encontrar imágenes con todos los tags
        images = []
        # Realiza la búsqueda no restringida
        images = Image.query.filter(Image.tags.any(Tag.name.in_(tags))).all()
    else:
        # Si no se proporcionan tags, mostrar un mensaje de error o redirigir a otra página
        # Aquí puedes agregar tu lógica según lo que desees hacer en este caso
        return "No se proporcionaron etiquetas para la búsqueda"

    return render_template('search_results.html', images=images, tags=tags)

# Definimos la nueva ruta para la búsqueda de múltiples tags restrictivo
@app.route('/search_by_multiple_tags_restrictive', methods=['GET'])
def search_by_multiple_tags_restrictive():
    # Obtener los tags especificados por el usuario desde la URL
    tags_input = request.args.get('tags')

    if tags_input:
        # Separar los tags por espacios
        tags = tags_input.split()
        
        # Realizar la búsqueda en la base de datos para encontrar imágenes con todos los tags
        images = []
        
        for image in Image.query.all():
            image_tags = [image_tag.name for image_tag in image.tags]
            if all(tag in image_tags for tag in tags):
                images.append(image)     
    else:
        # Si no se proporcionan tags, mostrar un mensaje de error o redirigir a otra página
        # Aquí puedes agregar tu lógica según lo que desees hacer en este caso
        return "No se proporcionaron etiquetas para la búsqueda"

    return render_template('search_results.html', images=images, tags=tags)

@app.route('/delete_tag', methods=['POST'])
def delete_tag():
    # Obtiene el nombre del tag a eliminar desde el formulario
    tag_name = request.form.get('tag_name')
    # print("Deleting tag:", tag_name)  # Impresión para depuración

    if tag_name:
        # Busca el tag en la base de datos
        tag = Tag.query.filter_by(name=tag_name).first()

        if tag:
            # print("Tag found:", tag.name)  # Impresión para depuración
            # Elimina el tag de la sesión de la base de datos
            db.session.delete(tag)
            db.session.commit()

            # Mensaje de éxito
            # flash(f'Se ha eliminado el tag "{tag_name}" correctamente.')
        else:
            # Mensaje de error si el tag no se encuentra
            flash(f'El tag "{tag_name}" no existe en la base de datos.')
    else:
        # Mensaje de error si no se proporciona un nombre de tag válido
        flash('No se ha proporcionado un nombre de tag válido.')

    # Redirige a la página principal u otra página según corresponda
    return redirect(url_for('index'))

@app.route('/add_tag_to_image/<int:image_id>', methods=['POST'])
def add_tag_to_image(image_id):
    # Obtener la entrada de texto del formulario y limpiarla
    new_tags_input = request.form['new_tag']
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s]+', ' ', new_tags_input)
    # Dividir la entrada de texto en tags por espacios
    new_tags = [tag.strip() for tag in cleaned_input.split()]

    # Procesar los tags
    for tag_name in new_tags:
        # Verificar si el tag ya existe en la base de datos
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            # Crear un nuevo tag si no existe
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.commit()

        # Verificar si ya existe la relación entre la imagen y el tag
        existing_association = ImageTagAssociation.query.filter_by(image_id=image_id, tag_id=tag.id).first()
        if not existing_association:
            # Crear la relación entre la imagen y el nuevo tag
            image_tag = ImageTagAssociation(image_id=image_id, tag_id=tag.id)
            db.session.add(image_tag)

    # Guardar todos los cambios en la base de datos al final
    db.session.commit()

    # Redirigir de vuelta a la página de la imagen
    return redirect(url_for('show_image', image_id=image_id))

@app.route('/update_image_url', methods=['POST'])
def update_image_url():
    new_url = request.form['new_url']
    image_id = request.form['image_id']
    print (new_url)
    print (image_id)

    # Actualizar la URL de la imagen en la base de datos
    image = Image.query.get(image_id)
    if image:
        image.url = new_url
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error='Imagen no encontrada')

@app.route('/show_image/<int:image_id>')
def show_image(image_id):
    # Obtén la imagen de la base de datos
    image = Image.query.get_or_404(image_id)
    
    # Obtén la lista de tags asociados a la imagen
    tags = [tag.name for tag in image.tags]

    # Renderiza la plantilla para mostrar la imagen y los tags
    return render_template('show_image.html', image=image, tags=tags)

@app.route('/add_url_to_image/<int:image_id>', methods=['POST'])
def add_url_to_image(image_id):
    # Obtener la URL de la imagen del formulario
    new_url = request.form.get('new_url')

    # Obtener la imagen de la base de datos
    image = Image.query.get(image_id)

    if image:
        # Actualizar la URL de la imagen
        image.url = new_url
        db.session.commit()
        flash('URL de la imagen actualizada con éxito', 'success')
    else:
        flash('Error: No se encontró la imagen correspondiente', 'error')

    # Redirigir de vuelta a la página de la imagen
    return redirect(url_for('show_image', image_id=image_id))

@app.route('/copy_image_url', methods=['POST'])
def copy_image_url():
    image_id = request.form['image_id']
    image = Image.query.get(image_id)
    if image and image.url:
        # Lógica para copiar la URL al portapapeles
        # Aquí puedes utilizar alguna biblioteca de JavaScript para copiar al portapapeles
        # Por ejemplo, utilizando el objeto navigator.clipboard de JavaScript
        return jsonify({'success': True, 'url': image.url})
    else:
        return jsonify({'success': False, 'error': 'Image URL not found'})

# Ruta para servir archivos desde la carpeta uploads
@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/images_without_tags')
def images_without_tags():
    # Consultar la base de datos para obtener las imágenes sin tags asociados
    images_without_tags = Image.query.filter_by(tags=None).all()
    return render_template('images_without_tags.html', images=images_without_tags)

@app.route('/delete_image_tag', methods=['POST'])
def delete_image_tag():
    # Obtener el ID de la imagen y el nombre del tag a eliminar desde el formulario
    image_id = request.form.get('image_id')
    tag_name = request.form.get('tag_name')

    if image_id and tag_name:
        # Buscar la imagen y el tag en la base de datos
        image = Image.query.get(image_id)
        tag = Tag.query.filter_by(name=tag_name).first()

        if image and tag:
            # Eliminar la asociación entre la imagen y el tag
            association = ImageTagAssociation.query.filter_by(image_id=image.id, tag_id=tag.id).first()
            if association:
                db.session.delete(association)
                db.session.commit()

                # flash(f'Se ha eliminado la asociación del tag "{tag_name}" de la imagen correctamente.')
            else:
                flash(f'La imagen no tiene el tag "{tag_name}" asociado.')
        else:
            flash('La imagen o el tag especificado no existen.')
    else:
        flash('No se proporcionó un ID de imagen o nombre de tag válido.')

    # Redirigir a la página de la imagen
    return redirect(url_for('show_image', image_id=image_id))


@app.route('/delete_image', methods=['POST'])
def delete_image():
    # Obtener el ID de la imagen a eliminar desde el formulario
    image_id = request.form.get('image_id')

    if image_id:
        # Buscar la imagen en la base de datos
        image = Image.query.get(image_id)

        if image:
            # Eliminar la imagen del disco
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            # Eliminar la imagen de la base de datos
            db.session.delete(image)
            db.session.commit()

            # Mensaje de éxito
            # flash('La imagen ha sido eliminada correctamente.')
        else:
            # Mensaje de error si la imagen no se encuentra
            flash('La imagen no existe en la base de datos.')
    else:
        # Mensaje de error si no se proporciona un ID de imagen válido
        flash('No se ha proporcionado un ID de imagen válido.')

    # Redirigir a la página principal u otra página según corresponda
    return redirect(url_for('index'))

# Define la nueva ruta para la galería
@app.route('/gallery')
def gallery():
    # Recupera todas las imágenes desde la base de datos
    images = Image.query.all()
    # Renderiza la plantilla de la galería y pasa las imágenes
    return render_template('gallery.html', images=images)

# Ruta para servir favicon.ico desde la misma carpeta que app.py
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    # Obtén todos los registros de la tabla Tag desde la base de datos
    # tags = Tag.query.distinct(Tag.name).all()
    
    # # Procesa los resultados para construir la lista de tags
    # tag_names = [tag.name for tag in tags]
    
    # return render_template('index.html', tags=tag_names)

    # Obtener todos los tags
    all_tags = Tag.query.all()

    # Crear un diccionario para almacenar los recuentos de imágenes para cada tag
    tag_counts = {}

    # Calcular el recuento de imágenes para cada tag
    for tag in all_tags:
        # Obtener el número de imágenes asociadas al tag actual
        image_count = Image.query.filter(Image.tags.any(name=tag.name)).count()
        # Agregar el tag y su recuento de imágenes al diccionario
        tag_counts[tag.name] = image_count

    # Obtener los tags con imágenes asociadas
    tags_with_images = [tag for tag in all_tags if tag.images]

    # Obtener los tags sin imágenes asociadas
    tags_without_images = [tag for tag in all_tags if not tag.images]

    # Obtener todas las imágenes
    all_images = Image.query.all()

    # Obtener imágenes sin tags
    images_without_tags = [image for image in all_images if not image.tags]

    # Consulta para obtener el número de imágenes únicas asociadas a cada etiqueta
    subquery = db.session.query(ImageTagAssociation.tag_id, func.count(func.distinct(ImageTagAssociation.image_id)).label('count')).group_by(ImageTagAssociation.tag_id).subquery()
    tags_with_images_count = db.session.query(Tag, subquery.c.count).outerjoin(subquery, Tag.id == subquery.c.tag_id).order_by(subquery.c.count.desc()).all()

    return render_template('index.html', tags_with_images=tags_with_images, tags_without_images=tags_without_images, images_without_tags=images_without_tags, tag_counts=tag_counts, tags_with_images_count=tags_with_images_count)

if __name__ == '__main__':
    #create_app()
    app.run(debug=True, host='0.0.0.0')
    

