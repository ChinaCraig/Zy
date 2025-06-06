from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置文件
    load_dotenv('config.env')
    
    # 配置应用
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('DEBUG_MODE', 'true').lower() == 'true'
    
    # 启用CORS支持
    CORS(app)
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    return app 