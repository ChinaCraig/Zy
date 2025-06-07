"""
意图识别服务
用于识别用户输入中的意图类型
"""
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import re


class IntentType(Enum):
    """意图类型枚举"""
    CHAT = "chat"                      # 普通聊天
    KB_SEARCH = "kb_search"            # 知识库检索
    VECTOR_SEARCH = "vector_search"    # 向量库检索  
    MCP_CALL = "mcp_call"              # MCP调用
    VIRTUAL_HUMAN = "virtual_human"    # 虚拟人交互
    
    
@dataclass
class Intent:
    """意图对象"""
    type: IntentType
    confidence: float  # 置信度 0-1
    params: Dict      # 参数
    raw_text: str     # 原始文本片段
    

class IntentDetectionService:
    """意图识别服务"""
    
    def __init__(self):
        """初始化意图识别服务"""
        # 意图关键词映射
        self.intent_keywords = {
            IntentType.KB_SEARCH: [
                "查询", "搜索", "找", "知识库", "资料", "文档",
                "检索", "了解", "是什么", "什么是", "告诉我"
            ],
            IntentType.VECTOR_SEARCH: [
                "向量", "相似", "相关", "类似", "embedding",
                "语义搜索", "相似度", "匹配"
            ],
            IntentType.MCP_CALL: [
                "MCP", "调用", "执行", "运行", "使用工具",
                "工具", "API", "接口", "功能"
            ],
            IntentType.VIRTUAL_HUMAN: [
                "虚拟人", "数字人", "和他聊", "和她聊", "对话",
                "交流", "聊天", "互动", "虚拟助手",
                "转圈", "旋转", "转动", "开始转圈", "转起来", "旋转起来",
                "停止", "停下", "别转了", "停止转圈", "不要转了", "站好"
            ]
        }
        
        # 意图模式正则表达式
        self.intent_patterns = {
            IntentType.KB_SEARCH: [
                r"(查询|搜索|找).*(知识|资料|文档)",
                r"(帮我|请).*(查|找|搜索)",
                r"(什么是|是什么|了解).+",
            ],
            IntentType.VECTOR_SEARCH: [
                r"(向量|语义).*(搜索|检索|查找)",
                r"(相似|类似|相关).*(内容|文档|资料)",
            ],
            IntentType.MCP_CALL: [
                r"(调用|使用|执行).*(MCP|工具|功能)",
                r"MCP.*(调用|执行|运行)",
            ],
            IntentType.VIRTUAL_HUMAN: [
                r"(和|与|跟).*(虚拟人|数字人|他|她).*(聊|交流|对话)",
                r"虚拟人.*(互动|交流|聊天)",
                r"(转圈|旋转|转动|转起来|旋转起来)",
                r"(停止|停下|别转了|停止转圈|不要转了|站好)",
            ]
        }
        
    def detect_intents(self, user_message: str, context: Optional[List[Dict]] = None) -> List[Intent]:
        """
        识别用户消息中的意图
        
        Args:
            user_message: 用户输入的消息
            context: 对话上下文（可选）
            
        Returns:
            识别出的意图列表
        """
        intents = []
        
        # 1. 基于关键词的意图识别
        keyword_intents = self._detect_by_keywords(user_message)
        intents.extend(keyword_intents)
        
        # 2. 基于正则模式的意图识别
        pattern_intents = self._detect_by_patterns(user_message)
        intents.extend(pattern_intents)
        
        # 3. 基于上下文的意图推断
        if context:
            context_intents = self._detect_by_context(user_message, context)
            intents.extend(context_intents)
        
        # 4. 去重和合并意图
        merged_intents = self._merge_intents(intents)
        
        # 5. 如果没有识别到任何意图，默认为普通聊天
        if not merged_intents:
            merged_intents.append(Intent(
                type=IntentType.CHAT,
                confidence=1.0,
                params={},
                raw_text=user_message
            ))
        
        return sorted(merged_intents, key=lambda x: x.confidence, reverse=True)
    
    def _detect_by_keywords(self, message: str) -> List[Intent]:
        """基于关键词的意图识别"""
        intents = []
        message_lower = message.lower()
        
        for intent_type, keywords in self.intent_keywords.items():
            matched_keywords = []
            for keyword in keywords:
                if keyword in message_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                confidence = min(len(matched_keywords) * 0.3, 0.9)
                intents.append(Intent(
                    type=intent_type,
                    confidence=confidence,
                    params={"matched_keywords": matched_keywords},
                    raw_text=message
                ))
        
        return intents
    
    def _detect_by_patterns(self, message: str) -> List[Intent]:
        """基于正则模式的意图识别"""
        intents = []
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    intents.append(Intent(
                        type=intent_type,
                        confidence=0.8,
                        params={"matched_pattern": pattern, "match": match.group()},
                        raw_text=message
                    ))
                    break  # 每种意图类型只匹配一次
        
        return intents
    
    def _detect_by_context(self, message: str, context: List[Dict]) -> List[Intent]:
        """基于上下文的意图推断"""
        intents = []
        
        # 分析最近的对话历史
        recent_messages = context[-3:] if len(context) >= 3 else context
        
        # 简单的上下文推断规则
        for msg in recent_messages:
            if msg.get("role") == "user":
                prev_message = msg.get("content", "").lower()
                
                # 如果之前提到了某种意图相关的内容，当前消息可能是延续
                if "知识库" in prev_message or "查询" in prev_message:
                    if "这个" in message or "它" in message or "还有" in message:
                        intents.append(Intent(
                            type=IntentType.KB_SEARCH,
                            confidence=0.6,
                            params={"context_inferred": True},
                            raw_text=message
                        ))
                
                if "虚拟人" in prev_message:
                    if "继续" in message or "再" in message:
                        intents.append(Intent(
                            type=IntentType.VIRTUAL_HUMAN,
                            confidence=0.6,
                            params={"context_inferred": True},
                            raw_text=message
                        ))
        
        return intents
    
    def _merge_intents(self, intents: List[Intent]) -> List[Intent]:
        """合并和去重意图"""
        merged = {}
        
        for intent in intents:
            key = intent.type
            if key in merged:
                # 保留置信度更高的
                if intent.confidence > merged[key].confidence:
                    merged[key] = intent
                else:
                    # 合并参数
                    merged[key].params.update(intent.params)
            else:
                merged[key] = intent
        
        return list(merged.values())
    
    def extract_intent_params(self, intent: Intent, message: str) -> Dict:
        """
        提取意图相关的参数
        
        Args:
            intent: 意图对象
            message: 用户消息
            
        Returns:
            提取的参数字典
        """
        params = intent.params.copy()
        
        if intent.type == IntentType.KB_SEARCH:
            # 提取查询关键词
            search_terms = self._extract_search_terms(message)
            params["search_terms"] = search_terms
            
        elif intent.type == IntentType.VIRTUAL_HUMAN:
            # 提取虚拟人相关参数
            params["virtual_human_name"] = self._extract_virtual_human_name(message)
            
        elif intent.type == IntentType.MCP_CALL:
            # 提取MCP调用相关参数
            params["mcp_function"] = self._extract_mcp_function(message)
        
        return params
    
    def _extract_search_terms(self, message: str) -> List[str]:
        """提取搜索关键词"""
        # 移除意图相关的词汇，保留实际的搜索内容
        stop_words = ["查询", "搜索", "找", "帮我", "请", "什么是", "是什么"]
        words = message.split()
        
        search_terms = []
        for word in words:
            if word not in stop_words and len(word) > 1:
                search_terms.append(word)
        
        return search_terms
    
    def _extract_virtual_human_name(self, message: str) -> Optional[str]:
        """提取虚拟人名称"""
        # 这里可以根据实际的虚拟人名称列表进行匹配
        virtual_humans = ["小明", "小红", "助手", "数字人"]
        
        for name in virtual_humans:
            if name in message:
                return name
        
        return None
    
    def _extract_mcp_function(self, message: str) -> Optional[str]:
        """提取MCP功能名称"""
        # 这里可以根据实际的MCP功能列表进行匹配
        # 暂时返回None，实际使用时需要根据MCP配置来提取
        return None


# 单例实例
intent_detector = IntentDetectionService() 