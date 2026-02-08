import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-banking-key-do-not-share'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///omegabank.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
