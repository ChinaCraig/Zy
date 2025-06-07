"""
知识库检索意图处理器
处理知识库查询相关的请求
"""
import os
import dotenv
from typing import Dict, Any, Optional, List
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType


class KBSearchHandler(IntentHandlerBase):
    """知识库检索处理器"""
    
    def __init__(self):
        super().__init__()
        # 加载知识库配置
        self._load_kb_config()
        
        # TODO: 初始化知识库连接或服务
        self.kb_service = None  # 暂时为None，实际使用时需要注入
    
    def _load_kb_config(self):
        """加载知识库配置"""
        # 加载知识库配置文件
        kb_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "config", "config_knowledge.env")
        
        # 设置配置属性默认值
        self.kb_service_url = "http://localhost:8000/kb"
        self.kb_api_key = "your_kb_api_key_here"
        self.kb_max_results = 5
        self.kb_relevance_threshold = 0.7
        self.kb_ids = ["default"]
        self.kb_query_model = "gpt-3.5-turbo"
        self.kb_summarize_model = "gpt-4"
        self.kb_debug = False
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(kb_config_path):
            kb_config = dotenv.dotenv_values(kb_config_path)
            
            self.kb_service_url = kb_config.get("KB_SERVICE_URL", self.kb_service_url)
            self.kb_api_key = kb_config.get("KB_API_KEY", self.kb_api_key)
            self.kb_max_results = int(kb_config.get("KB_MAX_RESULTS", self.kb_max_results))
            self.kb_relevance_threshold = float(kb_config.get("KB_RELEVANCE_THRESHOLD", self.kb_relevance_threshold))
            
            kb_ids_str = kb_config.get("KB_IDS", "default")
            self.kb_ids = [kb_id.strip() for kb_id in kb_ids_str.split(",")]
            
            self.kb_query_model = kb_config.get("KB_QUERY_MODEL", self.kb_query_model)
            self.kb_summarize_model = kb_config.get("KB_SUMMARIZE_MODEL", self.kb_summarize_model)
            self.kb_debug = kb_config.get("KB_DEBUG", "false").lower() == "true"
        
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        return intent.type == IntentType.KB_SEARCH
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理知识库检索意图
        
        Args:
            intent: 意图对象
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # 提取搜索参数
            params = intent.params
            search_terms = params.get("search_terms", [])
            
            # 如果没有提取到搜索词，使用整个消息
            if not search_terms:
                search_query = message
            else:
                search_query = " ".join(search_terms)
            
            # 调用知识库检索服务
            search_results = await self._search_knowledge_base(search_query, context)
            
            # 格式化响应
            if search_results:
                response = await self._format_search_results(search_results)
            else:
                response = f"抱歉，在知识库中没有找到关于 '{search_query}' 的相关信息。"
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "intent_type": "kb_search",
                    "search_query": search_query,
                    "results_count": len(search_results),
                    "results": search_results
                },
                "need_continue": True  # 可能需要继续处理其他意图
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"知识库检索失败：{str(e)}",
                "error": str(e),
                "need_continue": False
            }
    
    async def _search_knowledge_base(self, query: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        执行知识库检索
        
        Args:
            query: 搜索查询
            context: 上下文
            
        Returns:
            搜索结果列表
        """
        # 从上下文中获取LLM服务（如果有）
        llm_service = context.get("llm_service") if context else None
        
        # 使用LLM提取搜索关键词
        extracted_keywords = []
        if llm_service:
            try:
                # 使用LLM服务提取关键词
                system_prompt = "你是一个专业的搜索关键词提取助手。你的任务是从用户的问题中提取最相关的搜索关键词，以便在知识库中搜索。"
                prompt = f"从以下问题中提取3-5个最相关的搜索关键词（以逗号分隔）：\n\n'{query}'"
                
                keywords_text = await llm_service.get_response(
                    system_prompt=system_prompt, 
                    prompt=prompt,
                    model=self.kb_query_model
                )
                
                if keywords_text:
                    extracted_keywords = [k.strip() for k in keywords_text.split(',')]
                    
                    if self.kb_debug:
                        print(f"提取的关键词: {extracted_keywords}")
            except Exception as e:
                print(f"提取关键词时出错: {str(e)}")
        
        # 拼接搜索查询
        search_query = query
        if extracted_keywords:
            search_query = " ".join(extracted_keywords)
        
        if self.kb_service:
            # 使用实际的知识库服务
            try:
                return await self.kb_service.search(
                    query=search_query,
                    kb_ids=self.kb_ids,
                    max_results=self.kb_max_results,
                    threshold=self.kb_relevance_threshold
                )
            except Exception as e:
                print(f"知识库搜索失败: {str(e)}")
                # 返回知识库未创建的提示信息
                return [{
                    "title": "知识库未创建",
                    "content": "知识库服务尚未创建，这是一个待完成的功能。",
                    "score": 1.0,
                    "source": "系统提示"
                }]
        else:
            # 返回知识库未创建的提示信息
            return [{
                "title": "知识库未创建",
                "content": "知识库服务尚未创建，这是一个待完成的功能。",
                "score": 1.0,
                "source": "系统提示"
            }]
    
    async def _format_search_results(self, results: List[Dict]) -> str:
        """
        格式化搜索结果为用户友好的响应
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的响应文本
        """
        if not results:
            return "没有找到相关结果。"
        
        # 检查是否是知识库未创建的提示信息
        if len(results) == 1 and results[0].get("title") == "知识库未创建":
            return "【提示】知识库功能尚未创建。系统目前无法进行知识库检索，这是一个待完成的功能。"
        
        # 提取搜索结果内容
        contents = []
        for result in results:
            title = result.get("title", "无标题")
            content = result.get("content", "")
            score = result.get("score", 0)
            source = result.get("source", "未知来源")
            
            contents.append(f"标题: {title}\n内容: {content}\n相关度: {score:.2f}\n来源: {source}")
        
        # 将结果传递给LLM进行总结
        try:
            # 从上下文中获取LLM服务（如果有）
            llm_service = context.get("llm_service") if context else None
            
            if llm_service:
                system_prompt = "你是一个专业的知识总结助手。你的任务是基于检索到的知识库内容，为用户提供准确、全面的回答。"
                prompt = f"基于以下知识库检索结果，请为用户提供一个全面、清晰的回答。请仅使用这些检索结果中的信息回答，不要添加未提及的内容。\n\n"
                prompt += "检索结果:\n"
                
                for i, content in enumerate(contents, 1):
                    prompt += f"[{i}] {content}\n\n"
                
                summary = await llm_service.get_response(
                    system_prompt=system_prompt,
                    prompt=prompt,
                    model=self.kb_summarize_model
                )
                
                if summary:
                    return summary
        except Exception as e:
            print(f"总结搜索结果时出错: {str(e)}")
        
        # 如果LLM总结失败，则返回格式化的结果
        response_parts = ["为您找到以下相关信息：\n"]
        
        for i, result in enumerate(results[:5], 1):  # 最多显示5个结果
            title = result.get("title", "无标题")
            content = result.get("content", "")
            score = result.get("score", 0)
            source = result.get("source", "未知来源")
            
            # 截断过长的内容
            if len(content) > 200:
                content = content[:200] + "..."
            
            response_parts.append(
                f"{i}. **{title}** (相关度: {score:.2f})\n"
                f"   来源: {source}\n"
                f"   {content}\n"
            )
        
        if len(results) > 5:
            response_parts.append(f"\n还有 {len(results) - 5} 个相关结果未显示。")
        
        return "\n".join(response_parts) 