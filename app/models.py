import requests
import json
import time
from app.config import config

class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.conversation_history = []
    
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
    
    async def get_response(self, user_message):
        """获取AI回复"""
        try:
            if config.current_provider == 'openai':
                return await self._call_openai(user_message)
            elif config.current_provider == 'anthropic':
                return await self._call_anthropic(user_message)
            elif config.current_provider == 'deepseek':
                return await self._call_deepseek(user_message)
            elif config.current_provider == 'local':
                return await self._call_local(user_message)
            else:
                return self._get_mock_response(user_message)
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
            self.add_to_history(user_message, ai_response)
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
            self.add_to_history(user_message, ai_response)
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
            self.add_to_history(user_message, ai_response)
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
            self.add_to_history(user_message, ai_response)
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
        self.add_to_history(user_message, ai_response)
        return ai_response
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self):
        """获取对话历史"""
        return self.conversation_history

# 全局AI模型管理器实例
ai_manager = AIModelManager() 