from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class DatabaseManager:
    _instance = None
    
    def __init__(self):
        if not DatabaseManager._instance:
            try:
                self.client = MongoClient('mongodb://localhost:27017')
                self.db = self.client['budadb']
                self.collection = self.db['Usuarios']
                DatabaseManager._instance = self
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {str(e)}")
                raise
    @staticmethod
    def serialize_object_id(item):
        """Convert ObjectId to string in a document"""
        if item.get('_id'):
            item['_id'] = str(item['_id'])
        return item
    def get_user_by_username(self, username):
        """Retrieve a user by username"""
        try:
            user = self.users_collection.find_one({"username": username})
            if user:
                return self.serialize_object_id(user)
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            raise
    def get_user_by_id(self, user_id):
        """Retrieve a user by ID"""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return self.serialize_object_id(user)
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            raise
    
    def verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by the user"""
        return stored_password == provided_password