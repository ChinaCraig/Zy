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
    
    # 初始化数据库管理器
    from app.app_config import config
    from app.config import init_db_manager
    init_db_manager(config)
    
    # 注册蓝图
    from app.routes import main, llm_bp, vision_bp, speech_bp
    app.register_blueprint(main)
    app.register_blueprint(llm_bp)
    app.register_blueprint(vision_bp)
    app.register_blueprint(speech_bp)
    
    return app 