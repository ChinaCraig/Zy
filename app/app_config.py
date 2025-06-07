import os
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    
    def __init__(self):
        # 重新加载配置文件
        load_dotenv('config.env', override=True)
        self.reload_config()
    
    def reload_config(self):
        """重新加载配置"""
        self.current_provider = os.environ.get('CURRENT_PROVIDER', 'openai')
        self.virtual_human_name = os.environ.get('VIRTUAL_HUMAN_NAME', 'Zy')
        self.personality = os.environ.get('VIRTUAL_HUMAN_PERSONALITY', '友善、聪明、乐于助人的AI助手')
        self.reply_style = os.environ.get('REPLY_STYLE', 'casual')
        self.enable_emotions = os.environ.get('ENABLE_EMOTIONS', 'true').lower() == 'true'
        self.enable_identity_verification = os.environ.get('ENABLE_IDENTITY_VERIFICATION', 'true').lower() == 'true'
        self.max_history = int(os.environ.get('MAX_CONVERSATION_HISTORY', '50'))
        self.chat_storage_limit = int(os.environ.get('CHAT_STORAGE_LIMIT', '100'))
        
        # ===========================================
        # 数据库配置 - Database Configuration
        # ===========================================
        # MySQL数据库配置
        self.db_host = os.environ.get('DB_HOST', 'localhost')
        self.db_port = int(os.environ.get('DB_PORT', '3306'))
        self.db_username = os.environ.get('DB_USERNAME', 'root')
        self.db_password = os.environ.get('DB_PASSWORD', '')
        self.db_name = os.environ.get('DB_NAME', 'virtual_human_chat')
        self.db_charset = os.environ.get('DB_CHARSET', 'utf8mb4')
        
        # 数据库连接池配置
        self.db_pool_size = int(os.environ.get('DB_POOL_SIZE', '5'))
        self.db_pool_timeout = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
        self.db_pool_recycle = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
        
        # 是否启用数据库存储
        self.enable_database_storage = os.environ.get('ENABLE_DATABASE_STORAGE', 'true').lower() == 'true'
        
        # 加载当前提供商的配置
        self._load_provider_config()
    
    def _load_provider_config(self):
        """加载当前提供商的配置"""
        if self.current_provider == 'openai':
            self.api_key = os.environ.get('OPENAI_API_KEY')
            self.base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            self.model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
            self.max_tokens = int(os.environ.get('OPENAI_MAX_TOKENS', '2000'))
            self.temperature = float(os.environ.get('OPENAI_TEMPERATURE', '0.7'))
            
        elif self.current_provider == 'anthropic':
            self.api_key = os.environ.get('ANTHROPIC_API_KEY')
            self.base_url = os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
            self.model = os.environ.get('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            self.max_tokens = int(os.environ.get('ANTHROPIC_MAX_TOKENS', '2000'))
            self.temperature = float(os.environ.get('ANTHROPIC_TEMPERATURE', '0.7'))
            
        elif self.current_provider == 'deepseek':
            self.api_key = os.environ.get('DEEPSEEK_API_KEY')
            self.base_url = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
            self.model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
            self.max_tokens = int(os.environ.get('DEEPSEEK_MAX_TOKENS', '2000'))
            self.temperature = float(os.environ.get('DEEPSEEK_TEMPERATURE', '0.7'))
            
        elif self.current_provider == 'baidu':
            self.api_key = os.environ.get('BAIDU_API_KEY')
            self.secret_key = os.environ.get('BAIDU_SECRET_KEY')
            self.model = os.environ.get('BAIDU_MODEL', 'ernie-bot-turbo')
            
        elif self.current_provider == 'alibaba':
            self.api_key = os.environ.get('ALIBABA_API_KEY')
            self.model = os.environ.get('ALIBABA_MODEL', 'qwen-turbo')
            
        elif self.current_provider == 'tencent':
            self.secret_id = os.environ.get('TENCENT_SECRET_ID')
            self.secret_key = os.environ.get('TENCENT_SECRET_KEY')
            self.model = os.environ.get('TENCENT_MODEL', 'hunyuan-standard')
            
        elif self.current_provider == 'local':
            self.base_url = os.environ.get('LOCAL_BASE_URL', 'http://localhost:11434/v1')
            self.model = os.environ.get('LOCAL_MODEL', 'llama2')
            self.api_key = os.environ.get('LOCAL_API_KEY')
    
    def get_available_providers(self):
        """获取可用的模型提供商列表"""
        return [
            {'id': 'openai', 'name': 'OpenAI GPT', 'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']},
            {'id': 'anthropic', 'name': 'Anthropic Claude', 'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']},
            {'id': 'deepseek', 'name': 'DeepSeek', 'models': ['deepseek-chat', 'deepseek-coder']},
            {'id': 'baidu', 'name': '百度文心一言', 'models': ['ernie-bot', 'ernie-bot-turbo', 'ernie-bot-4']},
            {'id': 'alibaba', 'name': '阿里通义千问', 'models': ['qwen-turbo', 'qwen-plus', 'qwen-max']},
            {'id': 'tencent', 'name': '腾讯混元', 'models': ['hunyuan-lite', 'hunyuan-standard', 'hunyuan-pro']},
            {'id': 'local', 'name': '本地模型', 'models': ['llama2', 'mistral', 'codellama']}
        ]
    
    def switch_provider(self, provider, model=None):
        """切换模型提供商"""
        # 更新环境变量
        os.environ['CURRENT_PROVIDER'] = provider
        if model:
            if provider == 'openai':
                os.environ['OPENAI_MODEL'] = model
            elif provider == 'anthropic':
                os.environ['ANTHROPIC_MODEL'] = model
            elif provider == 'deepseek':
                os.environ['DEEPSEEK_MODEL'] = model
            elif provider == 'baidu':
                os.environ['BAIDU_MODEL'] = model
            elif provider == 'alibaba':
                os.environ['ALIBABA_MODEL'] = model
            elif provider == 'tencent':
                os.environ['TENCENT_MODEL'] = model
            elif provider == 'local':
                os.environ['LOCAL_MODEL'] = model
        
        # 重新加载配置
        self.reload_config()
        
        # 更新config.env文件
        self._update_config_file(provider, model)
    
    def _update_config_file(self, provider, model):
        """更新配置文件"""
        try:
            with open('config.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 更新CURRENT_PROVIDER
            for i, line in enumerate(lines):
                if line.startswith('CURRENT_PROVIDER='):
                    lines[i] = f'CURRENT_PROVIDER={provider}\n'
                    break
            
            # 更新对应的模型配置
            if model:
                model_key = f'{provider.upper()}_MODEL'
                for i, line in enumerate(lines):
                    if line.startswith(f'{model_key}='):
                        lines[i] = f'{model_key}={model}\n'
                        break
            
            with open('config.env', 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"更新配置文件失败: {e}")

# 全局配置实例
config = Config() 