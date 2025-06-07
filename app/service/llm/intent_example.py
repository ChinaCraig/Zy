"""
意图识别系统使用示例
展示如何扩展和使用意图识别功能
"""

# 示例1: 创建自定义意图类型
from enum import Enum
from app.service.llm import IntentType, IntentHandlerBase, Intent, intent_handler_manager
from typing import Dict, Any, Optional


# 扩展意图类型（如果需要新的意图）
class CustomIntentType(Enum):
    """自定义意图类型"""
    CODE_GENERATION = "code_generation"  # 代码生成
    DATA_ANALYSIS = "data_analysis"      # 数据分析


# 示例2: 创建自定义意图处理器
class CodeGenerationHandler(IntentHandlerBase):
    """代码生成意图处理器示例"""
    
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        # 这里需要判断intent.type是否是CODE_GENERATION
        return getattr(intent.type, 'value', None) == 'code_generation'
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理代码生成请求"""
        try:
            # 提取编程语言和需求
            language = self._extract_language(message)
            requirement = self._extract_requirement(message)
            
            # 生成代码（这里是模拟）
            generated_code = f"""
# Language: {language}
# Requirement: {requirement}

def example_function():
    '''这是根据您的需求生成的示例代码'''
    pass
"""
            
            return {
                "success": True,
                "response": f"已为您生成{language}代码：\n```{language}\n{generated_code}\n```",
                "data": {
                    "language": language,
                    "code": generated_code
                },
                "need_continue": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"代码生成失败：{str(e)}",
                "error": str(e),
                "need_continue": False
            }
    
    def _extract_language(self, message: str) -> str:
        """提取编程语言"""
        languages = ["python", "javascript", "java", "go", "rust"]
        message_lower = message.lower()
        
        for lang in languages:
            if lang in message_lower:
                return lang
        
        return "python"  # 默认
    
    def _extract_requirement(self, message: str) -> str:
        """提取需求描述"""
        # 简单实现，实际应该更智能
        return message


# 示例3: 如何在路由中使用
def example_usage():
    """示例：如何在Flask路由中使用意图识别"""
    
    # 1. 基本使用 - 在现有的/llm/chat接口中启用意图识别
    request_data = {
        "message": "请帮我查询中药黄芪的功效，并跟虚拟人小爱聊聊它的历史",
        "enable_intent_detection": True,  # 启用意图识别
        "parallel_intents": True  # 并行处理多个意图
    }
    
    # 2. 单独使用意图检测API
    detect_request = {
        "message": "我想了解一下MCP的功能，然后调用天气查询",
        "context": []  # 可选的对话历史
    }
    
    # 3. 查看所有可用的意图处理器
    # GET /llm/intent/handlers
    
    return {
        "chat_with_intent": request_data,
        "detect_intent": detect_request
    }


# 示例4: 如何注册新的意图处理器
def register_custom_handler():
    """注册自定义处理器的示例"""
    
    # 创建处理器实例
    code_gen_handler = CodeGenerationHandler()
    
    # 注册到管理器（需要先扩展IntentType枚举）
    # intent_handler_manager.register_handler(CustomIntentType.CODE_GENERATION, code_gen_handler)
    
    print("自定义处理器注册完成")


# 示例5: 批量测试意图识别
def test_intent_detection():
    """测试各种意图识别场景"""
    
    test_messages = [
        # 普通聊天
        "你好，今天天气怎么样？",
        
        # 知识库检索
        "请帮我查询一下Python的装饰器是什么",
        
        # 向量搜索
        "找一些与机器学习相似的内容",
        
        # MCP调用
        "使用MCP调用天气查询功能",
        
        # 虚拟人交互
        "我想和虚拟人小爱聊聊天",
        
        # 多意图
        "查询黄芪的功效，然后让虚拟人给我讲讲中医养生",
        
        # 上下文推断
        "还有其他的吗？",  # 需要根据上下文判断
    ]
    
    from app.service.llm import intent_detector
    
    for msg in test_messages:
        intents = intent_detector.detect_intents(msg)
        print(f"\n消息: {msg}")
        print(f"识别到的意图:")
        for intent in intents:
            print(f"  - {intent.type.value} (置信度: {intent.confidence})")


# 示例6: 如何自定义意图识别规则
def customize_intent_detection():
    """自定义意图识别规则的示例"""
    
    from app.service.llm import intent_detector, IntentType
    
    # 添加新的关键词
    intent_detector.intent_keywords[IntentType.KB_SEARCH].extend([
        "百科", "wiki", "定义", "解释"
    ])
    
    # 添加新的正则模式
    intent_detector.intent_patterns[IntentType.MCP_CALL].append(
        r"(执行|运行|调用).*(功能|命令|指令)"
    )
    
    print("意图识别规则已更新")


if __name__ == "__main__":
    # 运行示例
    print("=== 意图识别系统使用示例 ===")
    
    # 测试意图检测
    test_intent_detection()
    
    # 展示如何使用
    usage = example_usage()
    print(f"\n使用示例: {usage}")
    
    # 自定义规则
    customize_intent_detection() 