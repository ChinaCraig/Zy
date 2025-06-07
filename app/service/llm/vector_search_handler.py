"""
向量库检索意图处理器
处理基于向量相似度的语义搜索请求
"""
import os
import dotenv
from typing import Dict, Any, Optional, List
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType


class VectorSearchHandler(IntentHandlerBase):
    """向量库检索处理器"""
    
    def __init__(self):
        super().__init__()
        # 加载向量库配置
        self._load_vector_config()
        
        # TODO: 初始化向量数据库连接或服务
        self.vector_db = None  # 暂时为None，实际使用时需要注入
        self.embedding_service = None  # 嵌入向量生成服务
    
    def _load_vector_config(self):
        """加载向量库配置"""
        # 加载向量库配置文件
        vector_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "config", "config_embedding.env")
        
        # 设置配置属性默认值
        self.vector_db_type = "milvus"
        self.vector_db_host = "localhost"
        self.vector_db_port = 19530
        self.vector_dimension = 768
        self.embedding_model = "text-embedding-ada-002"
        self.vector_max_results = 5
        self.vector_similarity_threshold = 0.75
        self.vector_collection_name = "default_vectors"
        self.vector_query_model = "gpt-3.5-turbo"
        self.vector_summarize_model = "gpt-4"
        self.enable_hybrid_search = True
        self.vector_debug = False
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(vector_config_path):
            vector_config = dotenv.dotenv_values(vector_config_path)
            
            self.vector_db_type = vector_config.get("VECTOR_DB_TYPE", self.vector_db_type)
            self.vector_db_host = vector_config.get("VECTOR_DB_HOST", self.vector_db_host)
            self.vector_db_port = int(vector_config.get("VECTOR_DB_PORT", self.vector_db_port))
            self.vector_dimension = int(vector_config.get("VECTOR_DIMENSION", self.vector_dimension))
            self.embedding_model = vector_config.get("EMBEDDING_MODEL", self.embedding_model)
            self.vector_max_results = int(vector_config.get("VECTOR_MAX_RESULTS", self.vector_max_results))
            self.vector_similarity_threshold = float(vector_config.get("VECTOR_SIMILARITY_THRESHOLD", self.vector_similarity_threshold))
            self.vector_collection_name = vector_config.get("VECTOR_COLLECTION_NAME", self.vector_collection_name)
            self.vector_query_model = vector_config.get("VECTOR_QUERY_MODEL", self.vector_query_model)
            self.vector_summarize_model = vector_config.get("VECTOR_SUMMARIZE_MODEL", self.vector_summarize_model)
            self.enable_hybrid_search = vector_config.get("ENABLE_HYBRID_SEARCH", "true").lower() == "true"
            self.vector_debug = vector_config.get("VECTOR_DEBUG", "false").lower() == "true"
        
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        return intent.type == IntentType.VECTOR_SEARCH
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理向量库检索意图
        
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
            
            # 生成查询向量
            query_vector = await self._generate_embedding(message, context)
            
            # 执行向量搜索
            search_results = await self._vector_search(
                query_vector, 
                top_k=params.get("top_k", self.vector_max_results),
                threshold=params.get("threshold", self.vector_similarity_threshold)
            )
            
            # 格式化响应
            if search_results:
                response = await self._format_vector_results(search_results, context)
            else:
                response = "未找到相似的内容。请尝试使用不同的描述。"
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "intent_type": "vector_search",
                    "query": message,
                    "results_count": len(search_results),
                    "results": search_results
                },
                "need_continue": True  # 可能需要继续处理其他意图
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"向量检索失败：{str(e)}",
                "error": str(e),
                "need_continue": False
            }
    
    async def _generate_embedding(self, text: str, context: Optional[Dict] = None) -> List[float]:
        """
        生成文本的嵌入向量
        
        Args:
            text: 输入文本
            context: 上下文
            
        Returns:
            嵌入向量
        """
        # 从上下文中获取LLM服务（如果有）
        llm_service = context.get("llm_service") if context else None
        
        # 使用LLM优化搜索查询
        optimized_text = text
        if llm_service:
            try:
                # 使用LLM服务优化查询
                system_prompt = "你是一个专业的向量搜索优化助手。你的任务是重写用户的查询，使其更适合向量搜索。"
                prompt = f"请重写以下查询，使其更适合语义向量搜索。保留关键概念，删除不必要的词语，保持简洁：\n\n'{text}'"
                
                optimized_query = await llm_service.get_response(
                    system_prompt=system_prompt, 
                    prompt=prompt,
                    model=self.vector_query_model
                )
                
                if optimized_query:
                    optimized_text = optimized_query
                    
                    if self.vector_debug:
                        print(f"原始查询: {text}")
                        print(f"优化查询: {optimized_text}")
            except Exception as e:
                print(f"优化查询时出错: {str(e)}")
        
        if self.embedding_service:
            # 使用实际的嵌入服务
            return await self.embedding_service.embed(optimized_text, model=self.embedding_model)
        else:
            # 返回模拟的向量（实际使用时需要真实的嵌入模型）
            import random
            return [random.random() for _ in range(self.vector_dimension)]  # 模拟向量
    
    async def _vector_search(self, query_vector: List[float], top_k: int = 5, threshold: float = 0.7) -> List[Dict]:
        """
        执行向量相似度搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回前k个结果
            threshold: 相似度阈值
            
        Returns:
            搜索结果列表
        """
        if self.vector_db:
            # 使用实际的向量数据库
            try:
                results = await self.vector_db.search(
                    vector=query_vector,
                    collection_name=self.vector_collection_name,
                    top_k=top_k,
                    threshold=threshold
                )
                return results
            except Exception as e:
                print(f"向量搜索失败: {str(e)}")
                # 返回向量库未创建的提示信息
                return [{
                    "id": "error_001",
                    "content": "向量库服务尚未创建，这是一个待完成的功能。",
                    "similarity": 1.0,
                    "metadata": {
                        "source": "系统提示",
                        "category": "错误"
                    }
                }]
        else:
            # 返回向量库未创建的提示信息
            return [{
                "id": "error_001",
                "content": "向量库服务尚未创建，这是一个待完成的功能。",
                "similarity": 1.0,
                "metadata": {
                    "source": "系统提示",
                    "category": "错误"
                }
            }]
    
    async def _format_vector_results(self, results: List[Dict], context: Optional[Dict] = None) -> str:
        """
        格式化向量搜索结果
        
        Args:
            results: 搜索结果列表
            context: 上下文
            
        Returns:
            格式化的响应文本
        """
        if not results:
            return "没有找到语义相似的内容。"
        
        # 检查是否是向量库未创建的提示信息
        if len(results) == 1 and results[0].get("id") == "error_001":
            return "【提示】向量库功能尚未创建。系统目前无法进行向量语义搜索，这是一个待完成的功能。"
        
        # 提取搜索结果内容
        contents = []
        for result in results:
            content = result.get("content", "")
            similarity = result.get("similarity", 0)
            metadata = result.get("metadata", {})
            source = metadata.get("source", "未知来源")
            category = metadata.get("category", "")
            
            contents.append(f"内容: {content}\n相似度: {similarity:.2f}\n来源: {source}\n类别: {category}")
        
        # 将结果传递给LLM进行总结
        try:
            # 从上下文中获取LLM服务（如果有）
            llm_service = context.get("llm_service") if context else None
            
            if llm_service:
                system_prompt = "你是一个专业的语义搜索结果总结助手。你的任务是基于向量搜索检索到的内容，为用户提供准确、全面的回答。"
                prompt = f"基于以下语义向量搜索结果，请为用户提供一个综合的回答。请注意，这些结果是基于语义相似度排序的，而不仅仅是关键词匹配。\n\n"
                prompt += "搜索结果:\n"
                
                for i, content in enumerate(contents, 1):
                    prompt += f"[{i}] {content}\n\n"
                
                summary = await llm_service.get_response(
                    system_prompt=system_prompt,
                    prompt=prompt,
                    model=self.vector_summarize_model
                )
                
                if summary:
                    return summary
        except Exception as e:
            print(f"总结向量搜索结果时出错: {str(e)}")
        
        # 如果LLM总结失败，则返回格式化的结果
        response_parts = ["基于语义相似度，为您找到以下相关内容：\n"]
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            similarity = result.get("similarity", 0)
            metadata = result.get("metadata", {})
            source = metadata.get("source", "未知来源")
            category = metadata.get("category", "")
            
            # 截断过长的内容
            if len(content) > 300:
                content = content[:300] + "..."
            
            response_parts.append(
                f"{i}. [{category}] 相似度: {similarity:.2%}\n"
                f"   来源: {source}\n"
                f"   内容: {content}\n"
            )
        
        response_parts.append("\n提示：向量搜索基于语义相似度，可能会找到表述不同但含义相近的内容。")
        
        return "\n".join(response_parts) 