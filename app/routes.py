from flask import Blueprint, render_template, request, jsonify, send_from_directory
import asyncio
import threading
from app.config import config
from app.models import ai_manager

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

@main.route('/api/chat', methods=['POST'])
def chat():
    """聊天API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 创建事件循环来运行异步函数
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(ai_manager.get_response(user_message))
            finally:
                loop.close()
        
        # 在线程中运行异步函数
        ai_response = run_async()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'provider': config.current_provider,
            'model': config.model,
            'virtual_human_name': config.virtual_human_name
        })
        
    except Exception as e:
        print(f"聊天API错误: {e}")
        return jsonify({
            'success': False,
            'error': f'抱歉，我现在有点困惑 😅 请稍后再试试吧！'
        }), 500

@main.route('/api/providers')
def get_providers():
    """获取可用的模型提供商"""
    try:
        providers = config.get_available_providers()
        return jsonify({
            'success': True,
            'providers': providers,
            'current_provider': config.current_provider,
            'current_model': config.model
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/switch_provider', methods=['POST'])
def switch_provider():
    """切换模型提供商"""
    try:
        data = request.get_json()
        provider = data.get('provider')
        model = data.get('model')
        
        if not provider:
            return jsonify({'error': '请选择模型提供商'}), 400
        
        # 切换提供商
        config.switch_provider(provider, model)
        
        return jsonify({
            'success': True,
            'message': f'已切换到 {provider} - {model or "默认模型"}',
            'current_provider': config.current_provider,
            'current_model': config.model
        })
        
    except Exception as e:
        print(f"切换提供商错误: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/chat_history')
def get_chat_history():
    """获取聊天历史"""
    try:
        history = ai_manager.get_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/clear_history', methods=['POST'])
def clear_chat_history():
    """清空聊天历史"""
    try:
        ai_manager.clear_history()
        return jsonify({
            'success': True,
            'message': '聊天历史已清空'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
                'current_provider': config.current_provider,
                'current_model': config.model,
                'max_history': config.max_history
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 