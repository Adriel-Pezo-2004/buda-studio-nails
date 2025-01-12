from flask import Flask, request, jsonify
from flask_cors import CORS
from database import DatabaseManager
import logging
from datetime import datetime, timedelta
from bson.errors import InvalidId
from bson import ObjectId
import jwt
from functools import wraps
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia esto por una clave secreta segura
# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
# Initialize database manager
db_manager = DatabaseManager()
# Error handler for invalid ObjectId
@app.errorhandler(InvalidId)
def handle_invalid_id(error):
    return jsonify({'error': 'Invalid requirement ID format'}), 400
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Falta token!'}), 403
        try:
            token = token.split(" ")[1]  # Remove 'Bearer' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db_manager.get_user_by_id(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token ha expirado'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token es inválido'}), 403
        except Exception as e:
            logger.error(f"Token error: {str(e)}")
            return jsonify({'error': 'Token es inválido'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
@app.route('/api/login', methods=['POST'])
def login():
    try:
        auth = request.json
        print("Datos recibidos:", auth)  # Para debug
        if not auth or not auth.get('username') or not auth.get('password'):
            return jsonify({'error': 'Falta usuario o contraseña'}), 401
        user = db_manager.get_user_by_username(auth.get('username'))
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        if not db_manager.verify_password(user['password'], auth.get('password')):
            return jsonify({'error': 'Contraseña inválida'}), 401
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    except Exception as e:
        print("Error:", str(e))  # Para debug
        return jsonify({'error': 'Autenticación fallida'}), 401
    
@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        token = request.headers.get('Authorization').split()[1]
        # Here you would handle token invalidation if you have a token blacklist
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 400
if __name__ == '__main__':
    app.run(debug=True, port=5000)