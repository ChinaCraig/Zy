"""
MCP调用意图处理器
处理MCP（Model Context Protocol）相关的功能调用请求
"""
import os
import dotenv
from typing import Dict, Any, Optional, List
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType


class MCPCallHandler(IntentHandlerBase):
    """MCP调用处理器"""
    
    def __init__(self):
        super().__init__()
        # 加载MCP配置
        self._load_mcp_config()
        
        # TODO: 初始化MCP客户端或服务
        self.mcp_client = None  # 暂时为None，实际使用时需要注入
        self.available_functions = {}  # 可用的MCP功能映射
    
    def _load_mcp_config(self):
        """加载MCP配置"""
        # 加载MCP配置文件
        mcp_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "config", "config_mcp.env")
        
        # 设置配置属性默认值
        self.mcp_service_url = "http://localhost:8080/mcp"
        self.mcp_api_key = "your_mcp_api_key_here"
        self.mcp_api_version = "v1"
        self.mcp_enabled_functions = ["get_weather", "get_time", "calculate", "translate"]
        self.mcp_debug = False
        self.mcp_timeout = 30
        self.mcp_max_concurrent_calls = 5
        self.mcp_analysis_model = "gpt-4"
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(mcp_config_path):
            mcp_config = dotenv.dotenv_values(mcp_config_path)
            
            self.mcp_service_url = mcp_config.get("MCP_SERVICE_URL", self.mcp_service_url)
            self.mcp_api_key = mcp_config.get("MCP_API_KEY", self.mcp_api_key)
            self.mcp_api_version = mcp_config.get("MCP_API_VERSION", self.mcp_api_version)
            
            mcp_functions_str = mcp_config.get("MCP_ENABLED_FUNCTIONS", "")
            if mcp_functions_str:
                self.mcp_enabled_functions = [f.strip() for f in mcp_functions_str.split(",")]
            
            self.mcp_debug = mcp_config.get("MCP_DEBUG", "false").lower() == "true"
            self.mcp_timeout = int(mcp_config.get("MCP_TIMEOUT", self.mcp_timeout))
            self.mcp_max_concurrent_calls = int(mcp_config.get("MCP_MAX_CONCURRENT_CALLS", self.mcp_max_concurrent_calls))
            self.mcp_analysis_model = mcp_config.get("MCP_ANALYSIS_MODEL", self.mcp_analysis_model)
        
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        return intent.type == IntentType.MCP_CALL
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理MCP调用意图
        
        Args:
            intent: 意图对象
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # 提取MCP调用参数
            params = intent.params
            mcp_function = params.get("mcp_function")
            
            # 从上下文中获取LLM服务（如果有）
            llm_service = context.get("llm_service") if context else None
            
            # 如果没有明确指定功能，尝试从消息中推断
            if not mcp_function:
                if llm_service:
                    # 使用LLM智能推断功能
                    available_functions = await self._get_available_functions()
                    
                    # 检查是否有可用的MCP功能
                    if len(available_functions) == 1 and available_functions[0].get("name") == "mcp_unavailable":
                        # MCP服务未创建，返回提示信息
                        response = self._format_available_functions(available_functions)
                        return {
                            "success": True,
                            "response": response,
                            "data": {
                                "intent_type": "mcp_call",
                                "mcp_function": None,
                                "available_functions": available_functions
                            },
                            "need_continue": True  # 可以继续处理其他意图
                        }
                    
                    # 构建功能描述
                    functions_desc = "\n".join([
                        f"- {func['name']}: {func['description']} (参数: {', '.join(func['parameters'])})"
                        for func in available_functions
                    ])
                    
                    system_prompt = "你是一个专业的MCP功能分析助手。你的任务是分析用户消息，确定用户想要使用哪个MCP功能。"
                    prompt = f"根据用户消息，判断用户最可能想要使用的MCP功能。可用的功能有:\n\n{functions_desc}\n\n用户消息: '{message}'\n\n"
                    prompt += "请只返回最匹配的功能名称，不要有其他文字。如果无法确定，请返回null。"
                    
                    inferred_function = await llm_service.get_response(
                        system_prompt=system_prompt,
                        prompt=prompt,
                        model=self.mcp_analysis_model
                    )
                    
                    if inferred_function and inferred_function.strip().lower() != "null":
                        # 清理可能的额外文本
                        inferred_function = inferred_function.strip().lower()
                        # 检查是否是有效的功能名称
                        valid_names = [f["name"] for f in available_functions]
                        if inferred_function in valid_names:
                            mcp_function = inferred_function
                        else:
                            # 尝试模糊匹配
                            for name in valid_names:
                                if name in inferred_function or inferred_function in name:
                                    mcp_function = name
                                    break
                
                # 如果LLM推断失败，使用简单的关键词匹配
                if not mcp_function:
                    mcp_function = await self._infer_mcp_function(message, context)
            
            if not mcp_function:
                # 列出可用的MCP功能
                available_functions = await self._get_available_functions()
                response = self._format_available_functions(available_functions)
            else:
                # 执行MCP调用
                call_result = await self._execute_mcp_call(
                    mcp_function, 
                    message, 
                    context
                )
                response = self._format_mcp_result(mcp_function, call_result)
            
            # 检查结果中是否表明MCP服务未创建
            if "MCP服务尚未创建" in response:
                need_continue = True  # 如果MCP未创建，可以继续处理其他意图
            else:
                need_continue = False  # 正常MCP调用是独立操作
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "intent_type": "mcp_call",
                    "mcp_function": mcp_function,
                    "available_functions": await self._get_available_functions()
                },
                "need_continue": need_continue
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"MCP调用失败：{str(e)}",
                "error": str(e),
                "need_continue": True  # 出错时可以继续处理其他意图
            }
    
    async def _infer_mcp_function(self, message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        从消息中推断要调用的MCP功能
        
        Args:
            message: 用户消息
            context: 上下文
            
        Returns:
            推断的功能名称
        """
        # TODO: 实现智能推断逻辑
        # 这里使用简单的关键词匹配
        
        function_keywords = {
            "天气": "get_weather",
            "时间": "get_time",
            "计算": "calculate",
            "翻译": "translate",
            "生成代码": "generate_code",
            "数据查询": "query_data",
            "文件操作": "file_operation"
        }
        
        message_lower = message.lower()
        for keyword, function_name in function_keywords.items():
            if keyword in message_lower:
                return function_name
        
        return None
    
    async def _get_available_functions(self) -> List[Dict]:
        """
        获取可用的MCP功能列表
        
        Returns:
            功能列表
        """
        if self.mcp_client:
            # 从实际的MCP客户端获取
            try:
                return await self.mcp_client.list_functions()
            except Exception as e:
                print(f"获取MCP功能列表失败: {str(e)}")
                # 返回MCP服务未创建的提示信息
                return [{
                    "name": "mcp_unavailable",
                    "description": "MCP服务尚未创建，这是一个待完成的功能。",
                    "parameters": []
                }]
        else:
            # 检查是否是MCP服务未创建的情况
            if not self.mcp_enabled_functions:
                return [{
                    "name": "mcp_unavailable",
                    "description": "MCP服务尚未创建，这是一个待完成的功能。",
                    "parameters": []
                }]
            
            # 返回配置中启用的功能列表
            functions_map = {
                "get_weather": {
                    "name": "get_weather",
                    "description": "获取指定地点的天气信息",
                    "parameters": ["location"]
                },
                "get_time": {
                    "name": "get_time",
                    "description": "获取指定时区的当前时间",
                    "parameters": ["timezone"]
                },
                "calculate": {
                    "name": "calculate",
                    "description": "执行数学计算",
                    "parameters": ["expression"]
                },
                "translate": {
                    "name": "translate",
                    "description": "翻译文本",
                    "parameters": ["text", "target_language"]
                },
                "generate_code": {
                    "name": "generate_code",
                    "description": "生成代码片段",
                    "parameters": ["language", "task_description"]
                },
                "query_data": {
                    "name": "query_data",
                    "description": "查询数据库中的数据",
                    "parameters": ["query", "database"]
                }
            }
            
            # 只返回配置中启用的功能
            available_functions = []
            for func_name in self.mcp_enabled_functions:
                if func_name in functions_map:
                    available_functions.append(functions_map[func_name])
            
            return available_functions
    
    async def _execute_mcp_call(self, function_name: str, message: str, context: Optional[Dict] = None) -> Dict:
        """
        执行MCP调用
        
        Args:
            function_name: 功能名称
            message: 用户消息
            context: 上下文
            
        Returns:
            调用结果
        """
        # 检查MCP服务是否未创建
        if function_name == "mcp_unavailable":
            return {
                "status": "error",
                "error": "MCP服务尚未创建",
                "message": "MCP服务尚未创建，这是一个待完成的功能。"
            }
        
        # 提取参数
        params = await self._extract_function_params(function_name, message, context)
        
        if self.mcp_client:
            # 使用实际的MCP客户端
            try:
                return await self.mcp_client.call_function(
                    function_name,
                    params,
                    timeout=self.mcp_timeout
                )
            except Exception as e:
                print(f"MCP调用失败: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                    "message": f"MCP服务调用失败: {str(e)}"
                }
        else:
            # 返回MCP服务未创建的提示信息
            return {
                "status": "error",
                "error": "MCP服务尚未创建",
                "message": "MCP服务尚未创建，这是一个待完成的功能。",
                "params": params
            }
    
    async def _extract_function_params(self, function_name: str, message: str, context: Optional[Dict] = None) -> Dict:
        """
        从消息中提取功能参数
        
        Args:
            function_name: 功能名称
            message: 用户消息
            context: 上下文
            
        Returns:
            参数字典
        """
        # 从上下文中获取LLM服务（如果有）
        llm_service = context.get("llm_service") if context else None
        
        # 使用LLM智能提取参数
        if llm_service:
            try:
                # 根据功能类型确定需要提取的参数
                parameters_info = {}
                for func in await self._get_available_functions():
                    if func["name"] == function_name:
                        parameters_info = {
                            "name": func["name"],
                            "description": func["description"],
                            "parameters": func["parameters"]
                        }
                        break
                
                if not parameters_info:
                    return {"message": message}
                
                # 构建提示
                param_list = ", ".join(parameters_info.get("parameters", []))
                system_prompt = "你是一个专业的参数提取助手。你的任务是从用户消息中提取指定功能所需的参数。"
                prompt = f"请从以下用户消息中提取\"{function_name}\"功能所需的参数: {param_list}\n\n用户消息: '{message}'\n\n"
                prompt += f"请以JSON格式返回提取的参数，格式为: {{\n"
                
                for param in parameters_info.get("parameters", []):
                    prompt += f'  "{param}": "提取的值",\n'
                
                prompt += "}\n\n如果无法提取某个参数，请将其值设为null。"
                
                params_text = await llm_service.get_response(
                    system_prompt=system_prompt,
                    prompt=prompt,
                    model=self.mcp_analysis_model
                )
                
                if params_text:
                    # 尝试解析为JSON
                    try:
                        import json
                        params = json.loads(params_text)
                        return params
                    except json.JSONDecodeError:
                        print(f"参数提取结果无法解析为JSON: {params_text}")
            except Exception as e:
                print(f"参数提取时出错: {str(e)}")
        
        # 如果LLM提取失败，返回简单的默认参数
        if function_name == "get_weather":
            return {"location": "北京"}
        elif function_name == "get_time":
            return {"timezone": "Asia/Shanghai"}
        elif function_name == "calculate":
            # 简单尝试提取表达式
            import re
            match = re.search(r'计算\s*([\d\+\-\*\/\(\)\s]+)', message)
            expression = match.group(1) if match else "1+1"
            return {"expression": expression}
        elif function_name == "translate":
            # 简单尝试提取目标语言
            target_lang = "英文" if "翻译成英文" in message or "翻译为英文" in message else "中文"
            return {"text": message, "target_language": target_lang}
        else:
            return {"message": message}
    
    def _format_available_functions(self, functions: List[Dict]) -> str:
        """
        格式化可用功能列表
        
        Args:
            functions: 功能列表
            
        Returns:
            格式化的文本
        """
        # 检查是否返回了MCP服务未创建的提示信息
        if len(functions) == 1 and functions[0].get("name") == "mcp_unavailable":
            return "【提示】MCP服务功能尚未创建。系统目前无法进行MCP功能调用，这是一个待完成的功能。"
        
        response_parts = ["以下是可用的MCP功能：\n"]
        
        for func in functions:
            name = func.get("name", "未知")
            description = func.get("description", "无描述")
            parameters = func.get("parameters", [])
            
            response_parts.append(
                f"• **{name}**: {description}\n"
                f"  参数: {', '.join(parameters) if parameters else '无'}\n"
            )
        
        response_parts.append("\n您可以说明要使用哪个功能，我会帮您调用。")
        
        return "\n".join(response_parts)
    
    def _format_mcp_result(self, function_name: str, result: Dict) -> str:
        """
        格式化MCP调用结果
        
        Args:
            function_name: 功能名称
            result: 调用结果
            
        Returns:
            格式化的响应
        """
        # 检查是否是MCP服务未创建的错误消息
        if result.get("status") == "error" and "MCP服务尚未创建" in result.get("error", ""):
            return "【提示】MCP服务功能尚未创建。系统目前无法进行MCP功能调用，这是一个待完成的功能。"
        
        if result.get("status") == "success":
            data = result.get("data", {})
            
            # 根据不同的功能格式化结果
            if function_name == "get_weather":
                return (
                    f"🌤️ {data.get('location', '未知地点')}的天气：\n"
                    f"温度：{data.get('temperature', '未知')}\n"
                    f"天气：{data.get('weather', '未知')}\n"
                    f"湿度：{data.get('humidity', '未知')}"
                )
            elif function_name == "get_time":
                return (
                    f"🕐 {data.get('timezone', '未知时区')}的当前时间：\n"
                    f"{data.get('time', '未知')}"
                )
            elif function_name == "calculate":
                return (
                    f"🧮 计算结果：\n"
                    f"{data.get('expression', '未知')} = {data.get('result', '未知')}"
                )
            elif function_name == "translate":
                return (
                    f"🌐 翻译结果：\n"
                    f"原文：{data.get('original', '未知')}\n"
                    f"译文（{data.get('target_language', '未知')}）：{data.get('translated', '未知')}"
                )
            elif function_name == "generate_code":
                return (
                    f"💻 生成的代码（{data.get('language', '未知语言')}）：\n\n"
                    f"```{data.get('language', '')}\n{data.get('code', '// 无代码生成')}\n```\n\n"
                    f"说明：{data.get('explanation', '')}"
                )
            elif function_name == "query_data":
                return (
                    f"📊 数据查询结果：\n"
                    f"查询：{data.get('query', '未知查询')}\n"
                    f"结果数量：{data.get('count', 0)}\n\n"
                    f"{data.get('results', '无结果')}"
                )
            else:
                return f"MCP调用成功：\n{data}"
        else:
            error = result.get("error", "未知错误")
            message = result.get("message", "")
            
            if message:
                return f"MCP调用失败：{message}"
            else:
                return f"MCP调用失败：{error}" 