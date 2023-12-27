from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from bson import ObjectId
from pymongo import MongoClient

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Configuración de la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client['document_repository']
documents_collection = db['documents']

# Rutas y funciones asociadas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/categories')
def categories():
    categories = documents_collection.distinct('category')
    return render_template('categories.html', categories=categories)

@app.route('/my_documents')
def my_documents():
    documents = documents_collection.find()
    delete_document_url = url_for('delete_document', document_id='')  # Asegúrate de proporcionar un valor predeterminado para document_id
    return render_template('my_documents.html', documents=documents, delete_document_url=delete_document_url)

@app.route('/edit_document/<document_id>', methods=['POST'])
def edit_document(document_id):
    if document_id is None or document_id.lower() == 'null':
        return jsonify({'success': False, 'error': 'Invalid document_id'})

    try:
        document = documents_collection.find_one({'_id': ObjectId(document_id)})
        # Resto de la lógica...
    except ObjectId.errors.InvalidId:
        return jsonify({'success': False, 'error': 'Invalid ObjectId format'})

@app.route('/delete_document/<document_id>', methods=['POST'])
def delete_document(document_id):
    try:
        result = documents_collection.delete_one({'_id': ObjectId(document_id)})
        if result.deleted_count == 1:
            return {'success': True}
        else:
            return {'success': False, 'error': 'Documento no encontrado'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/toggle_favorite/<document_id>', methods=['POST'])
def toggle_favorite(document_id):
    try:
        document = documents_collection.find_one({'_id': ObjectId(document_id)})

        if document:
            new_favorite_state = not document.get('favorite', False)
            documents_collection.update_one({'_id': ObjectId(document_id)}, {'$set': {'favorite': new_favorite_state}})

            return {'success': True, 'favorite': new_favorite_state}

        return {'success': False, 'error': 'Documento no encontrado'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/favorite_documents')
def favorite_documents():
    favorite_documents = documents_collection.find({'favorite': True})
    return render_template('favorite_documents.html', favorite_documents=favorite_documents)

@app.route('/add_document', methods=['GET', 'POST'])
def add_document():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']

        # Puedes agregar más campos según tus necesidades

        document_data = {
            'title': title,
            'category': category,
            # Agrega más campos aquí
        }

        documents_collection.insert_one(document_data)
        return redirect(url_for('my_documents'))

    return render_template('add_document.html')

if __name__ == '__main__':
    app.run(debug=True)
