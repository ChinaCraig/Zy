import requests
import json
import time
from app.app_config import config
from app.models.chat_models import chat_archive_service

class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_identity = None  # 用户身份信息
        self.is_identity_verified = False  # 身份验证状态
        self.chat_terminated = False  # 聊天是否被终止
        self.session_info = {}  # 会话信息（浏览器、IP等）
    
    def add_to_history(self, user_message, ai_response):
        """添加对话到历史记录"""
        self.conversation_history.append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': time.time()
        })
        
        # 限制历史记录长度
        if len(self.conversation_history) > config.max_history:
            self.conversation_history = self.conversation_history[-config.max_history:]
        
        # 检查是否达到聊天存储上限
        if len(self.conversation_history) >= config.chat_storage_limit:
            self.chat_terminated = True
    
    def get_system_prompt(self):
        """获取系统提示词"""
        style_prompts = {
            'formal': '请用正式、专业的语言回复。',
            'casual': '请用轻松、友好的语言回复。',
            'cute': '请用可爱、俏皮的语言回复，可以适当使用颜文字。'
        }
        
        system_prompt = f"""
你是{config.virtual_human_name}，{config.personality}。
{style_prompts.get(config.reply_style, '')}
请保持回复简洁有趣，长度控制在100字以内。
"""
        
        if config.enable_emotions:
            system_prompt += "请在回复中表达适当的情感，让对话更加生动。"
        
        return system_prompt.strip()
    
    def verify_identity(self, user_input):
        """验证用户身份"""
        if not user_input or not user_input.strip():
            return False, "请输入您的姓名。"
        
        name = user_input.strip()
        
        # 基本验证规则
        if len(name) > 20:
            return False, "姓名太长了，请输入一个简短的名字。"
        
        if len(name) < 1:
            return False, "请输入您的姓名。"
        
        # 检查是否包含过多特殊字符
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?/~`'
        special_count = sum(1 for char in name if char in special_chars)
        if special_count > 2:
            return False, "姓名中特殊字符太多，请输入一个正常的名字。"
        
        # 检查是否全是数字
        if name.isdigit():
            return False, "请输入您的姓名，而不是纯数字。"
        
        # 检查是否是常见的无意义输入
        meaningless_inputs = [
            'test', 'testing', '测试', 'aaa', 'abc', 
            'hello', 'hi', '你好', 'qwerty', 'asdf', '...', '。。。',
            'user', 'admin', 'root', 'guest'
        ]
        if name.lower() in meaningless_inputs:
            return False, "请输入您的真实姓名或昵称，而不是测试内容。"
        
        # 检查是否全是相同字符
        if len(set(name)) == 1 and len(name) > 3:
            return False, "请输入一个正常的姓名。"
        
        # 验证通过
        self.user_identity = name
        self.is_identity_verified = True
        return True, None
    
    def reset_identity(self):
        """重置身份验证状态"""
        self.user_identity = None
        self.is_identity_verified = False
        self.chat_terminated = False
        self.session_info = {}  # 清空会话信息
    
    def get_identity_prompt(self):
        """获取身份确认提示"""
        style_prompts = {
            'formal': '欢迎使用！为了更好地为您服务，请先告诉我您的姓名或昵称。',
            'casual': f'嗨～我是{config.virtual_human_name}！请告诉我你的名字，这样我就知道怎么称呼你了～😊',
            'cute': f'你好呀～我是{config.virtual_human_name}！可以告诉我你的名字吗？我想认识你呢～ ✨'
        }
        return style_prompts.get(config.reply_style, '请输入您的姓名以开始对话。')
    
    def get_termination_message(self):
        """获取聊天终止提示信息"""
        style_messages = {
            'formal': f'很抱歉，我们的对话已达到存储上限（{config.chat_storage_limit}条记录）。请清空聊天历史或重启应用以继续对话。感谢您的理解。',
            'casual': f'哎呀～我们聊得太多了！已经达到{config.chat_storage_limit}条记录的上限了 😅 需要清空一下聊天记录才能继续哦～',
            'cute': f'呀～我们聊了好多好多话呢！已经有{config.chat_storage_limit}条记录啦 (＞﹏＜) 需要清理一下小脑袋才能继续聊天哦～'
        }
        return style_messages.get(config.reply_style, f'对话已达到存储上限（{config.chat_storage_limit}条记录），请清空历史后继续。')
    
    def detect_goodbye_intent(self, user_message):
        """检测用户是否想结束聊天"""
        goodbye_keywords = [
            '再见', '拜拜', '结束', '退出', '离开', '下线', '关闭',
            'bye', 'goodbye', 'exit', 'quit', 'close', 'end',
            '88', '886', '晚安', '睡觉', '休息', '走了', '先走了',
            '不聊了', '聊天结束', '结束聊天', '停止聊天'
        ]
        
        message_lower = user_message.lower().strip()
        return any(keyword in message_lower for keyword in goodbye_keywords)
    
    def get_response_sync(self, user_message):
        """获取AI回复（同步版本）"""
        try:
            # 检查聊天是否已终止
            if self.chat_terminated:
                return self.get_termination_message()
            
            # 检查身份验证
            if config.enable_identity_verification and not self.is_identity_verified:
                # 尝试验证身份
                is_valid, error_message = self.verify_identity(user_message)
                if is_valid:
                    welcome_messages = {
                        'formal': f'您好，{self.user_identity}！很高兴认识您。有什么可以为您做的吗？',
                        'casual': f'嗨 {self.user_identity}！很开心认识你～有什么想聊的吗？😊',
                        'cute': f'哇～原来你叫{self.user_identity}呀！好好听的名字～我是{config.virtual_human_name}，以后请多多指教哦 ✨'
                    }
                    # 身份验证成功，记录到历史但不调用AI
                    welcome_msg = welcome_messages.get(config.reply_style, f'您好，{self.user_identity}！很高兴认识您。')
                    # 手动添加到历史记录
                    self.conversation_history.append({
                        'user': user_message,
                        'assistant': welcome_msg,
                        'timestamp': time.time()
                    })
                    return welcome_msg
                else:
                    # 身份验证失败，直接返回错误提示，不调用AI也不记录历史
                    if error_message:
                        return error_message
                    else:
                        return self.get_identity_prompt()
            
            # 检测是否是告别意图
            if self.detect_goodbye_intent(user_message):
                # 先获取AI回复
                if config.current_provider == 'openai':
                    response = self._call_openai_sync(user_message)
                elif config.current_provider == 'anthropic':
                    response = self._call_anthropic_sync(user_message)
                elif config.current_provider == 'deepseek':
                    response = self._call_deepseek_sync(user_message)
                elif config.current_provider == 'local':
                    response = self._call_local_sync(user_message)
                else:
                    response = self._get_mock_response(user_message)
                
                # 添加到历史记录
                self.add_to_history(user_message, response)
                
                # 归档聊天记录
                self.clear_history('user_goodbye')
                
                return response
            
            # 正常处理AI回复
            if config.current_provider == 'openai':
                response = self._call_openai_sync(user_message)
            elif config.current_provider == 'anthropic':
                response = self._call_anthropic_sync(user_message)
            elif config.current_provider == 'deepseek':
                response = self._call_deepseek_sync(user_message)
            elif config.current_provider == 'local':
                response = self._call_local_sync(user_message)
            else:
                response = self._get_mock_response(user_message)
            
            # 添加到历史记录
            self.add_to_history(user_message, response)
            return response
        except Exception as e:
            print(f"AI调用出错: {e}")
            return f"抱歉，我现在有点困惑 😅 请稍后再试试吧！"

    async def get_response(self, user_message):
        """获取AI回复"""
        try:
            # 检查聊天是否已终止
            if self.chat_terminated:
                return self.get_termination_message()
            
            # 检查身份验证
            if config.enable_identity_verification and not self.is_identity_verified:
                # 尝试验证身份
                is_valid, error_message = self.verify_identity(user_message)
                if is_valid:
                    welcome_messages = {
                        'formal': f'您好，{self.user_identity}！很高兴认识您。有什么可以为您做的吗？',
                        'casual': f'嗨 {self.user_identity}！很开心认识你～有什么想聊的吗？😊',
                        'cute': f'哇～原来你叫{self.user_identity}呀！好好听的名字～我是{config.virtual_human_name}，以后请多多指教哦 ✨'
                    }
                    # 身份验证成功，记录到历史但不调用AI
                    welcome_msg = welcome_messages.get(config.reply_style, f'您好，{self.user_identity}！很高兴认识您。')
                    # 手动添加到历史记录
                    self.conversation_history.append({
                        'user': user_message,
                        'assistant': welcome_msg,
                        'timestamp': time.time()
                    })
                    return welcome_msg
                else:
                    # 身份验证失败，直接返回错误提示，不调用AI也不记录历史
                    if error_message:
                        return error_message
                    else:
                        return self.get_identity_prompt()
            
            # 检测是否是告别意图
            if self.detect_goodbye_intent(user_message):
                # 先获取AI回复
                if config.current_provider == 'openai':
                    response = await self._call_openai(user_message)
                elif config.current_provider == 'anthropic':
                    response = await self._call_anthropic(user_message)
                elif config.current_provider == 'deepseek':
                    response = await self._call_deepseek(user_message)
                elif config.current_provider == 'local':
                    response = await self._call_local(user_message)
                else:
                    response = self._get_mock_response(user_message)
                
                # 添加到历史记录
                self.add_to_history(user_message, response)
                
                # 归档聊天记录
                self.clear_history('user_goodbye')
                
                return response
            
            # 正常处理AI回复
            if config.current_provider == 'openai':
                response = await self._call_openai(user_message)
            elif config.current_provider == 'anthropic':
                response = await self._call_anthropic(user_message)
            elif config.current_provider == 'deepseek':
                response = await self._call_deepseek(user_message)
            elif config.current_provider == 'local':
                response = await self._call_local(user_message)
            else:
                response = self._get_mock_response(user_message)
            
            # 添加到历史记录
            self.add_to_history(user_message, response)
            return response
        except Exception as e:
            print(f"AI调用出错: {e}")
            return f"抱歉，我现在有点困惑 😅 请稍后再试试吧！"
    
    async def _call_openai(self, user_message):
        """调用OpenAI API"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:  # 只保留最近5轮对话
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.model,
            'messages': messages,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"OpenAI API错误: {response.status_code}")
    
    async def _call_anthropic(self, user_message):
        """调用Anthropic API"""
        headers = {
            'x-api-key': config.api_key,
            'content-type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # 构建对话历史
        conversation = self.get_system_prompt() + "\n\n"
        for conv in self.conversation_history[-5:]:
            conversation += f"Human: {conv['user']}\n\nAssistant: {conv['assistant']}\n\n"
        conversation += f"Human: {user_message}\n\nAssistant:"
        
        data = {
            'model': config.model,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'messages': [{"role": "user", "content": conversation}]
        }
        
        response = requests.post(
            f'{config.base_url}/v1/messages',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['content'][0]['text'].strip()
            return ai_response
        else:
            raise Exception(f"Anthropic API错误: {response.status_code}")
    
    async def _call_deepseek(self, user_message):
        """调用DeepSeek API"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:  # 只保留最近5轮对话
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.model,
            'messages': messages,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
    
    async def _call_local(self, user_message):
        """调用本地模型API"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {'Content-Type': 'application/json'}
        if config.api_key:
            headers['Authorization'] = f'Bearer {config.api_key}'
        
        data = {
            'model': config.model,
            'messages': messages,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"本地模型API错误: {response.status_code}")
    
    def _call_openai_sync(self, user_message):
        """调用OpenAI API（同步版本）"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:  # 只保留最近5轮对话
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.model,
            'messages': messages,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"OpenAI API错误: {response.status_code}")
    
    def _call_anthropic_sync(self, user_message):
        """调用Anthropic API（同步版本）"""
        headers = {
            'x-api-key': config.api_key,
            'content-type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # 构建对话历史
        conversation = self.get_system_prompt() + "\n\n"
        for conv in self.conversation_history[-5:]:
            conversation += f"Human: {conv['user']}\n\nAssistant: {conv['assistant']}\n\n"
        conversation += f"Human: {user_message}\n\nAssistant:"
        
        data = {
            'model': config.model,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'messages': [{"role": "user", "content": conversation}]
        }
        
        response = requests.post(
            f'{config.base_url}/v1/messages',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['content'][0]['text'].strip()
            return ai_response
        else:
            raise Exception(f"Anthropic API错误: {response.status_code}")
    
    def _call_deepseek_sync(self, user_message):
        """调用DeepSeek API（同步版本）"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:  # 只保留最近5轮对话
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.model,
            'messages': messages,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
    
    def _call_local_sync(self, user_message):
        """调用本地模型API（同步版本）"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 添加历史对话
        for conv in self.conversation_history[-5:]:
            messages.append({"role": "user", "content": conv['user']})
            messages.append({"role": "assistant", "content": conv['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        headers = {'Content-Type': 'application/json'}
        if config.api_key:
            headers['Authorization'] = f'Bearer {config.api_key}'
        
        data = {
            'model': config.model,
            'messages': messages,
            'stream': False
        }
        
        response = requests.post(
            f'{config.base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            return ai_response
        else:
            raise Exception(f"本地模型API错误: {response.status_code}")

    def _get_mock_response(self, user_message):
        """模拟回复（用于测试）"""
        mock_responses = [
            f"你好！我是{config.virtual_human_name}，很高兴和你聊天！😊",
            "这是一个很有趣的问题呢～我正在思考中...",
            "哇，你说得很有道理！我学到了新东西 ✨",
            "让我想想...嗯，我觉得可能是这样的...",
            "真是太棒了！感谢你和我分享这些 💫"
        ]
        
        import random
        ai_response = random.choice(mock_responses)
        return ai_response
    
    def clear_history(self, end_reason='user_clear'):
        """清空对话历史并归档"""
        # 如果有聊天记录且用户已验证身份，则归档到数据库
        if self.conversation_history and self.is_identity_verified:
            try:
                # 转换历史记录格式以适配数据库
                formatted_history = []
                for conv in self.conversation_history:
                    formatted_history.append({
                        'role': 'user',
                        'content': conv['user']
                    })
                    formatted_history.append({
                        'role': 'assistant', 
                        'content': conv['assistant']
                    })
                
                # 归档聊天记录
                success = chat_archive_service.archive_chat_session(
                    conversation_history=formatted_history,
                    user_identity=self.user_identity,
                    ai_provider=config.current_provider,
                    ai_model=config.model,
                    end_reason=end_reason,
                    browser_info=self.session_info.get('browser_info'),
                    ip_address=self.session_info.get('ip_address'),
                    location_info=self.session_info.get('location_info')
                )
                
                if success:
                    print(f"聊天记录已成功归档到数据库，用户: {self.user_identity}, 消息数: {len(self.conversation_history)}")
                else:
                    print(f"聊天记录归档失败，用户: {self.user_identity}, 消息数: {len(self.conversation_history)}")
            except Exception as e:
                print(f"归档聊天记录失败: {e}")
        
        # 清空内存中的历史记录
        self.conversation_history = []
        self.reset_identity()  # 重置身份验证状态
    
    def get_history(self):
        """获取对话历史"""
        return {
            'history': self.conversation_history,
            'user_identity': self.user_identity,
            'is_identity_verified': self.is_identity_verified,
            'chat_terminated': self.chat_terminated,
            'chat_count': len(self.conversation_history),
            'chat_limit': config.chat_storage_limit,
            'session_info': self.session_info
        }
    
    def set_session_info(self, browser_info: str = None, ip_address: str = None, location_info: str = None):
        """设置会话信息"""
        if browser_info:
            self.session_info['browser_info'] = browser_info
        if ip_address:
            self.session_info['ip_address'] = ip_address
        if location_info:
            self.session_info['location_info'] = location_info

# 全局AI模型管理器实例
ai_manager = AIModelManager() 