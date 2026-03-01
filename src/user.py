import pandas as pd
import mysql.connector
import db.database as db
from src.transaction import Transaction

class User:
    def __init__(self, user_id, username, email, password, birthday, is_active=True):
        self.user_id = user_id
        self._username = username
        self._email = email
        self._password = password
        self.birthday = birthday
        self.is_active = is_active


    @property
    def username(self):
        return self._username 

    @username.setter
    def username(self, value):
        if not value:
            raise ValueError("Username cannot be empty.")
        self._username = value
        db.update_username(self.user_id, self._username)  

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value:
            raise ValueError("Email cannot be empty.")
        self._email = value
        db.update_user_email(self.user_id, self._email) 

    @property
    def password(self):
        return self._password  
    
    @password.setter
    def password(self, value):
        if not value:
            raise ValueError("Password cannot be empty.")
        self._password = value
        db.update_user_password(self.user_id, self._password)