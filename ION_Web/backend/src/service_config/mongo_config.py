from pymongo import MongoClient
import os
from uuid import uuid4, UUID
from typing import Tuple, Optional, Union
from obj_types import User, ChatHistory, APIResponse

class MongoDBClient:
    def __init__(self):
        print(os.getenv('MONGODB_CONNECTION_STRING'))
        self.client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
        self.db = self.client['ion-web-db']
        self.users = self.db['Users']

    def add_user(self, email: str) -> Tuple[UUID, str, int]:
        """Add a new user or return existing user"""
        print(f"Attempting to add/find user with email: {email}")
        user = self.users.find_one({'Email': email})
        print(f"Existing user data: {user}")
        
        if user:
            if 'user_id' in user:
                print(f"Found existing user with ID: {user['user_id']}")
                return UUID(user['user_id']), 'User already exists', 200
            else:
                user_id = uuid4()
                print(f"Updating existing user with new ID: {user_id}")
                self.users.update_one(
                    {'Email': email}, 
                    {'$set': {'user_id': str(user_id)}}
                )
                return user_id, 'User already exists', 200
        else:
            user_id = uuid4()
            print(f"Creating new user with ID: {user_id}")
            # Create User model first
            new_user = User(
                email=email,
                user_id=user_id,
                traces={},
                messages={}
            )
            # Convert to dict and map fields for MongoDB
            user_data = {
                'Email': new_user.email,  # Convert 'email' to 'Email' for MongoDB
                'user_id': str(new_user.user_id),
                'traces': new_user.traces,
                'messages': new_user.messages
            }
            print(f"Inserting user data: {user_data}")
            self.users.insert_one(user_data)
            return user_id, 'User added successfully', 201

    def get_user(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Get user by user_id"""
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        print(f"Looking for user with ID: {user_id}")
        user_data = self.users.find_one({'user_id': user_id})
        print(f"Found user data: {user_data}")
        
        if user_data:
            try:
                # Map MongoDB fields to Pydantic model fields
                print(f"Attempting to create User model with email: {user_data.get('Email')}")
                user = User(
                    email=user_data['Email'],  # Convert 'Email' to 'email'
                    user_id=user_id,
                    traces=user_data.get('traces', {}),
                    messages=user_data.get('messages', {})
                )
                print(f"Successfully created User model: {user}")
                return user
            except Exception as e:
                print(f"Error creating User model: {str(e)}")
                print(f"User data keys: {user_data.keys()}")
                raise
        print("No user found")
        return None

    def update_chat_history(self, user_id: Union[str, UUID], 
                          history_id: str, 
                          chat_history: dict) -> Tuple[bool, str, int]:
        """Update chat history for a user"""
        user = self.get_user(user_id)
        if not user:
            return False, 'User not found', 404
        
        try:
            messages = user.messages or {}
            messages[history_id] = chat_history
            result = self.users.update_one(
                {'user_id': str(user_id)}, 
                {'$set': {'messages': messages}}
            )
            if result.modified_count > 0:
                return True, 'Chat history updated successfully', 200
            return False, 'No changes made to chat history', 304
        except Exception as e:
            print(f"Error updating chat history: {e}")
            return False, 'Failed to update chat history', 500
