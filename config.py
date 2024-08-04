import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'debian'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    BASE_URL = ''  # 默认值
    HOST = '0.0.0.0'
    PORT = 8052
