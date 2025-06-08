from flask import Blueprint, render_template, request, jsonify, send_from_directory
from app.app_config import config

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """主页"""
    return render_template('index.html', 
                         virtual_human_name=config.virtual_human_name,
                         current_provider=config.current_provider,
                         current_model=config.model)

@main.route('/models/<filename>')
def serve_model(filename):
    """提供VRM模型文件"""
    return send_from_directory('static/models', filename)



def get_client_ip():
    """获取客户端IP地址"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')

@main.route('/api/config')
def get_config():
    """获取当前配置"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'virtual_human_name': config.virtual_human_name,
                'personality': config.personality,
                'reply_style': config.reply_style,
                'enable_emotions': config.enable_emotions,
                'enable_identity_verification': config.enable_identity_verification,
                'current_provider': config.current_provider,
                'current_model': config.model,
                'max_history': config.max_history,
                'chat_storage_limit': config.chat_storage_limit
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
