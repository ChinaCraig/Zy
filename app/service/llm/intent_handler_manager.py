"""
意图处理器管理器
负责注册、管理和调度所有的意图处理器
"""
from typing import Dict, List, Type, Optional, Any
import asyncio
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType, intent_detector

# 导入所有的处理器
from .chat_handler import ChatHandler
from .kb_search_handler import KBSearchHandler
from .vector_search_handler import VectorSearchHandler
from .mcp_call_handler import MCPCallHandler
from .virtual_human_handler import VirtualHumanHandler


class IntentHandlerManager:
    """意图处理器管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.handlers: Dict[IntentType, IntentHandlerBase] = {}
        self.intent_detector = intent_detector
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认的处理器"""
        # 创建并注册所有默认处理器
        self.register_handler(IntentType.CHAT, ChatHandler())
        self.register_handler(IntentType.KB_SEARCH, KBSearchHandler())
        self.register_handler(IntentType.VECTOR_SEARCH, VectorSearchHandler())
        self.register_handler(IntentType.MCP_CALL, MCPCallHandler())
        self.register_handler(IntentType.VIRTUAL_HUMAN, VirtualHumanHandler())
    
    def register_handler(self, intent_type: IntentType, handler: IntentHandlerBase):
        """
        注册意图处理器
        
        Args:
            intent_type: 意图类型
            handler: 处理器实例
        """
        if not isinstance(handler, IntentHandlerBase):
            raise ValueError(f"处理器必须继承自IntentHandlerBase: {type(handler)}")
        
        self.handlers[intent_type] = handler
        print(f"已注册意图处理器: {intent_type.value} -> {handler}")
    
    def unregister_handler(self, intent_type: IntentType):
        """
        注销意图处理器
        
        Args:
            intent_type: 意图类型
        """
        if intent_type in self.handlers:
            del self.handlers[intent_type]
            print(f"已注销意图处理器: {intent_type.value}")
    
    def get_handler(self, intent_type: IntentType) -> Optional[IntentHandlerBase]:
        """
        获取指定意图类型的处理器
        
        Args:
            intent_type: 意图类型
            
        Returns:
            处理器实例，如果不存在返回None
        """
        return self.handlers.get(intent_type)
    
    async def process_message(
        self, 
        message: str, 
        context: Optional[Dict] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        处理用户消息，识别意图并调用相应的处理器
        
        Args:
            message: 用户消息
            context: 上下文信息
            parallel: 是否并行处理多个意图
            
        Returns:
            处理结果
        """
        # 1. 识别意图
        # 从context中提取对话历史（如果有的话）
        conversation_history = context.get("conversation_history", []) if context else []
        intents = self.intent_detector.detect_intents(message, conversation_history)
        
        if not intents:
            return {
                "success": False,
                "response": "无法识别您的意图，请重新表述。",
                "intents": []
            }
        
        # 2. 提取每个意图的参数
        for intent in intents:
            intent.params = self.intent_detector.extract_intent_params(intent, message)
        
        # 3. 处理意图
        results = []
        
        if parallel and len(intents) > 1:
            # 并行处理多个意图
            results = await self._process_intents_parallel(intents, message, context)
        else:
            # 顺序处理意图
            results = await self._process_intents_sequential(intents, message, context)
        
        # 4. 合并结果
        final_result = self._merge_results(results, intents)
        
        return final_result
    
    async def _process_intents_parallel(
        self, 
        intents: List[Intent], 
        message: str, 
        context: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """
        并行处理多个意图
        
        Args:
            intents: 意图列表
            message: 用户消息
            context: 上下文
            
        Returns:
            处理结果列表
        """
        tasks = []
        
        for intent in intents:
            handler = self.get_handler(intent.type)
            if handler and handler.can_handle(intent):
                task = handler.execute(intent, message, context)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 过滤掉异常结果
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                elif isinstance(result, Exception):
                    valid_results.append({
                        "success": False,
                        "response": f"处理出错: {str(result)}",
                        "error": str(result)
                    })
            return valid_results
        
        return []
    
    async def _process_intents_sequential(
        self, 
        intents: List[Intent], 
        message: str, 
        context: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """
        顺序处理意图
        
        Args:
            intents: 意图列表
            message: 用户消息
            context: 上下文
            
        Returns:
            处理结果列表
        """
        results = []
        
        for intent in intents:
            handler = self.get_handler(intent.type)
            if handler and handler.can_handle(intent):
                try:
                    result = await handler.execute(intent, message, context)
                    results.append(result)
                    
                    # 如果处理器指示不需要继续，则停止
                    if not result.get("need_continue", True):
                        break
                        
                except Exception as e:
                    results.append({
                        "success": False,
                        "response": f"处理出错: {str(e)}",
                        "error": str(e)
                    })
        
        return results
    
    def _merge_results(self, results: List[Dict[str, Any]], intents: List[Intent]) -> Dict[str, Any]:
        """
        合并多个处理结果
        
        Args:
            results: 处理结果列表
            intents: 意图列表
            
        Returns:
            合并后的最终结果
        """
        if not results:
            return {
                "success": False,
                "response": "没有可用的处理器来处理您的请求。",
                "intents": [{"type": intent.type.value, "confidence": intent.confidence} for intent in intents]
            }
        
        # 合并所有响应
        merged_response = []
        all_data = {}
        overall_success = True
        
        for i, result in enumerate(results):
            if result.get("success", False):
                response = result.get("response", "")
                if response:
                    # 如果只有一个意图，不添加标签前缀
                    if len(results) == 1:
                        merged_response.append(response)
                    else:
                        intent_type = intents[i].type.value if i < len(intents) else "unknown"
                        merged_response.append(f"【{intent_type}】\n{response}")
                
                # 合并数据
                if "data" in result:
                    if len(results) == 1:
                        # 单个意图时，直接使用result中的data
                        all_data = result["data"]
                    else:
                        # 多个意图时，分别存储
                        all_data[f"intent_{i}"] = result["data"]
            else:
                overall_success = False
                error_msg = result.get("response", "处理失败")
                merged_response.append(f"❌ {error_msg}")
        
        # 构建最终响应
        final_response = "\n\n---\n\n".join(merged_response) if merged_response else "处理完成，但没有生成响应。"
        
        return {
            "success": overall_success,
            "response": final_response,
            "intents": [
                {
                    "type": intent.type.value,
                    "confidence": intent.confidence,
                    "params": intent.params
                } for intent in intents
            ],
            "data": all_data,
            "results_count": len(results)
        }
    
    def list_handlers(self) -> List[Dict[str, str]]:
        """
        列出所有已注册的处理器
        
        Returns:
            处理器信息列表
        """
        return [
            {
                "intent_type": intent_type.value,
                "handler_name": handler.__class__.__name__,
                "handler_repr": str(handler)
            }
            for intent_type, handler in self.handlers.items()
        ]


# 创建全局管理器实例
intent_handler_manager = IntentHandlerManager() 