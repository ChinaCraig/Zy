"""
大语言模型相关路由
"""
from flask import Blueprint, request, jsonify
from app.app_config import config
from app.models import ai_manager

llm_bp = Blueprint('llm', __name__, url_prefix='/llm')

def get_client_ip():
    """获取客户端IP地址"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')

@llm_bp.route('/chat', methods=['POST'])
def chat():
    """聊天API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 获取会话信息
        browser_info = request.headers.get('User-Agent', 'unknown')
        ip_address = get_client_ip()
        
        # 设置会话信息（仅在首次设置时）
        if not ai_manager.session_info.get('browser_info'):
            ai_manager.set_session_info(
                browser_info=browser_info,
                ip_address=ip_address
            )
        
        # 使用同步版本
        ai_response = ai_manager.get_response_sync(user_message)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'provider': config.current_provider,
            'model': config.model,
            'virtual_human_name': config.virtual_human_name
        })
        
    except Exception as e:
        import traceback
        print(f"聊天API错误: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'抱歉，我现在有点困惑 😅 请稍后再试试吧！'
        }), 500

@llm_bp.route('/providers', methods=['GET'])
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

@llm_bp.route('/switch_provider', methods=['POST'])
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

@llm_bp.route('/chat_history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    try:
        history_data = ai_manager.get_history()
        return jsonify({
            'success': True,
            **history_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/clear_history', methods=['POST'])
def clear_chat_history():
    """清空聊天历史"""
    try:
        # 更健壮的JSON解析
        try:
            data = request.get_json(force=True, silent=True) or {}
        except Exception as json_error:
            print(f"JSON解析错误: {json_error}")
            data = {}
        
        end_reason = data.get('end_reason', 'user_clear')
        
        # 确保会话信息已设置（用于归档）
        if not ai_manager.session_info.get('browser_info'):
            browser_info = request.headers.get('User-Agent', 'unknown')
            ip_address = get_client_ip()
            ai_manager.set_session_info(
                browser_info=browser_info,
                ip_address=ip_address
            )
        
        ai_manager.clear_history(end_reason)
        return jsonify({
            'success': True,
            'message': '聊天历史已清空并归档'
        })
    except Exception as e:
        import traceback
        print(f"清空历史错误: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/identity_status', methods=['GET'])
def get_identity_status():
    """获取身份验证状态"""
    try:
        return jsonify({
            'success': True,
            'is_identity_verified': ai_manager.is_identity_verified,
            'user_identity': ai_manager.user_identity,
            'chat_terminated': ai_manager.chat_terminated,
            'chat_count': len(ai_manager.conversation_history),
            'chat_limit': config.chat_storage_limit,
            'enable_identity_verification': config.enable_identity_verification,
            'identity_prompt': ai_manager.get_identity_prompt() if not ai_manager.is_identity_verified else None,
            'session_info': ai_manager.session_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/set_session_info', methods=['POST'])
def set_session_info():
    """设置会话信息（浏览器、IP等）"""
    try:
        data = request.get_json() or {}
        
        # 自动获取IP和浏览器信息
        browser_info = request.headers.get('User-Agent', 'unknown')
        ip_address = get_client_ip()
        
        # 可选：从客户端获取地理位置信息
        location_info = data.get('location_info')
        
        ai_manager.set_session_info(
            browser_info=browser_info,
            ip_address=ip_address,
            location_info=location_info
        )
        
        return jsonify({
            'success': True,
            'message': '会话信息已设置',
            'session_info': ai_manager.session_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/chat_archive/user/<user_identity>', methods=['GET'])
def get_user_chat_archive(user_identity):
    """获取用户的聊天归档历史"""
    try:
        from app.models.chat_models import chat_archive_service
        
        limit = request.args.get('limit', 10, type=int)
        history = chat_archive_service.get_user_chat_history(user_identity, limit)
        
        return jsonify({
            'success': True,
            'user_identity': user_identity,
            'chat_history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/chat_archive/session/<session_id>', methods=['GET'])
def get_session_detail(session_id):
    """获取特定会话的详细信息"""
    try:
        from app.models.chat_models import chat_archive_service
        
        detail = chat_archive_service.get_session_detail(session_id)
        
        if not detail:
            return jsonify({'success': False, 'error': '会话不存在'}), 404
        
        return jsonify({
            'success': True,
            'session_detail': detail
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 兼容原有API路径的路由 (重定向或代理)
@llm_bp.route('/generate', methods=['POST'])
def generate():
    """
    大语言模型生成接口 (预留扩展)
    """
    # 暂时重定向到chat接口，后续可以实现专门的生成逻辑
    return chat()

@llm_bp.route('/complete', methods=['POST'])
def complete():
    """
    大语言模型文本补全接口 (预留扩展)
    """
    # 暂时重定向到chat接口，后续可以实现专门的补全逻辑
    return chat() 