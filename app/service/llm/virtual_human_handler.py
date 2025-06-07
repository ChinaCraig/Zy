"""
虚拟人交互意图处理器
处理与虚拟人/数字人的交互请求
"""
import os
import re
import dotenv
from typing import Dict, Any, Optional, List, Set
from .intent_handler_base import IntentHandlerBase
from .intent_detection_service import Intent, IntentType


class VirtualHumanHandler(IntentHandlerBase):
    """虚拟人交互处理器"""
    
    def __init__(self):
        super().__init__()
        # 加载虚拟人配置
        self._load_virtual_human_config()
        
        # TODO: 初始化虚拟人服务
        self.virtual_human_service = None  # 暂时为None，实际使用时需要注入
        self.available_virtual_humans = {}  # 可用的虚拟人配置
    
    def _load_virtual_human_config(self):
        """加载虚拟人配置"""
        # 加载虚拟人配置文件
        virtual_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      "config", "config_virtual.env")
        
        # 设置配置属性默认值
        self.virtual_human_service_url = "http://localhost:9000/virtual"
        self.virtual_human_api_key = "your_virtual_human_api_key"
        self.default_virtual_human = "xiaojia"
        
        # 虚拟人动作配置
        self.actions = {"spin": "1", "stop": "0"}
        
        # 动作对应的指令集
        self.spin_commands: Set[str] = {"转圈", "旋转", "转动", "开始转圈", "转起来", "旋转起来"}
        self.stop_commands: Set[str] = {"停止", "停下", "别转了", "停止转圈", "不要转了", "站好"}
        
        # 其他配置
        self.virtual_human_model_path = "/models/virtual_human_default.glb"
        self.virtual_human_render_quality = "high"
        self.virtual_human_shadow_enabled = True
        self.virtual_human_voice_enabled = True
        self.virtual_human_voice_type = "female_zh"
        self.virtual_human_response_model = "gpt-3.5-turbo"
        self.virtual_human_action_model = "gpt-4"
        self.virtual_human_debug = False
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(virtual_config_path):
            virtual_config = dotenv.dotenv_values(virtual_config_path)
            
            self.virtual_human_service_url = virtual_config.get("VIRTUAL_HUMAN_SERVICE_URL", self.virtual_human_service_url)
            self.virtual_human_api_key = virtual_config.get("VIRTUAL_HUMAN_API_KEY", self.virtual_human_api_key)
            self.default_virtual_human = virtual_config.get("DEFAULT_VIRTUAL_HUMAN", self.default_virtual_human)
            
            # 解析动作配置
            actions_str = virtual_config.get("VIRTUAL_HUMAN_ACTIONS", "spin=1,stop=0")
            for action_pair in actions_str.split(","):
                if "=" in action_pair:
                    action_name, action_code = action_pair.split("=", 1)
                    self.actions[action_name.strip()] = action_code.strip()
            
            # 解析指令集
            spin_commands_str = virtual_config.get("SPIN_COMMANDS", "")
            if spin_commands_str:
                self.spin_commands = set(cmd.strip() for cmd in spin_commands_str.split(","))
                
            stop_commands_str = virtual_config.get("STOP_COMMANDS", "")
            if stop_commands_str:
                self.stop_commands = set(cmd.strip() for cmd in stop_commands_str.split(","))
            
            # 其他配置
            self.virtual_human_model_path = virtual_config.get("VIRTUAL_HUMAN_MODEL_PATH", self.virtual_human_model_path)
            self.virtual_human_render_quality = virtual_config.get("VIRTUAL_HUMAN_RENDER_QUALITY", self.virtual_human_render_quality)
            self.virtual_human_shadow_enabled = virtual_config.get("VIRTUAL_HUMAN_SHADOW_ENABLED", "true").lower() == "true"
            self.virtual_human_voice_enabled = virtual_config.get("VIRTUAL_HUMAN_VOICE_ENABLED", "true").lower() == "true"
            self.virtual_human_voice_type = virtual_config.get("VIRTUAL_HUMAN_VOICE_TYPE", self.virtual_human_voice_type)
            self.virtual_human_response_model = virtual_config.get("VIRTUAL_HUMAN_RESPONSE_MODEL", self.virtual_human_response_model)
            self.virtual_human_action_model = virtual_config.get("VIRTUAL_HUMAN_ACTION_MODEL", self.virtual_human_action_model)
            self.virtual_human_debug = virtual_config.get("VIRTUAL_HUMAN_DEBUG", "false").lower() == "true"
        
    def can_handle(self, intent: Intent) -> bool:
        """判断是否可以处理该意图"""
        return intent.type == IntentType.VIRTUAL_HUMAN
    
    async def handle(self, intent: Intent, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理虚拟人交互意图
        
        Args:
            intent: 意图对象
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # 提取虚拟人参数
            params = intent.params
            virtual_human_name = params.get("virtual_human_name")
            
            # 如果没有指定虚拟人，使用默认或让用户选择
            if not virtual_human_name:
                virtual_human_name = await self._select_virtual_human(message, context)
            
            # 检查是否是虚拟人动作指令
            action_type, _ = self._detect_action_command(message)
            has_action = action_type is not None
            
            if not virtual_human_name and not has_action:
                # 列出可用的虚拟人
                available_humans = await self._get_available_virtual_humans()
                response = self._format_available_humans(available_humans)
                action_data = None
            else:
                # 如果是动作指令但没有指定虚拟人，使用默认虚拟人
                if has_action and not virtual_human_name:
                    virtual_human_name = self.default_virtual_human
                    
                # 与虚拟人交互
                interaction_result = await self._interact_with_virtual_human(
                    virtual_human_name,
                    message,
                    context
                )
                
                # 格式化交互结果
                response = self._format_interaction_result(
                    virtual_human_name,
                    interaction_result
                )
                
                # 如果是动作指令，将动作代码添加到返回数据中
                if has_action and "action_code" in interaction_result:
                    action_data = {
                        "action": action_type,
                        "action_code": interaction_result["action_code"]
                    }
                else:
                    action_data = None
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "intent_type": "virtual_human",
                    "virtual_human": virtual_human_name,
                    "interaction_mode": params.get("interaction_mode", "text"),
                    "action": action_data
                },
                "need_continue": not has_action  # 如果是动作指令，不需要继续其他操作
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"虚拟人交互失败：{str(e)}",
                "error": str(e),
                "need_continue": True  # 出错时可以继续处理其他意图
            }
    
    async def _select_virtual_human(self, message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        选择或推断要交互的虚拟人
        
        Args:
            message: 用户消息
            context: 上下文
            
        Returns:
            虚拟人名称
        """
        # 从上下文中获取默认虚拟人
        if context and "default_virtual_human" in context:
            return context["default_virtual_human"]
        
        # 从配置中获取默认虚拟人
        available_humans = await self._get_available_virtual_humans()
        if available_humans:
            # 返回第一个可用的虚拟人作为默认
            return available_humans[0]["name"]
        
        return None
    
    async def _get_available_virtual_humans(self) -> List[Dict]:
        """
        获取可用的虚拟人列表
        
        Returns:
            虚拟人列表
        """
        if self.virtual_human_service:
            # 从实际的服务获取
            try:
                return await self.virtual_human_service.list_virtual_humans()
            except Exception as e:
                print(f"获取虚拟人列表失败: {str(e)}")
                # 返回默认的虚拟人
                return [{
                    "name": self.default_virtual_human,
                    "avatar": "default.png",
                    "personality": "友善、耐心",
                    "specialties": ["聊天", "转圈"],
                    "voice": self.virtual_human_voice_type
                }]
        else:
            # 返回默认的虚拟人
            return [{
                "name": self.default_virtual_human,
                "avatar": "default.png",
                "personality": "友善、耐心",
                "specialties": ["聊天", "转圈"],
                "voice": self.virtual_human_voice_type,
                "actions": list(self.actions.keys())
            }]
    
    async def _interact_with_virtual_human(
        self, 
        virtual_human_name: str, 
        message: str, 
        context: Optional[Dict] = None
    ) -> Dict:
        """
        与虚拟人进行交互
        
        Args:
            virtual_human_name: 虚拟人名称
            message: 用户消息
            context: 上下文
            
        Returns:
            交互结果
        """
        # 检查是否是虚拟人动作指令
        action_type, action_text = self._detect_action_command(message)
        
        if self.virtual_human_service:
            # 使用实际的虚拟人服务
            try:
                # 如果检测到动作指令，执行动作
                if action_type:
                    return await self.virtual_human_service.execute_action(
                        virtual_human_name,
                        action_type,
                        context
                    )
                # 否则执行普通交互
                else:
                    return await self.virtual_human_service.interact(
                        virtual_human_name,
                        message,
                        context
                    )
            except Exception as e:
                print(f"虚拟人交互失败: {str(e)}")
                # 返回交互失败的提示
                return {
                    "text": f"虚拟人交互失败: {str(e)}",
                    "emotion": "sad",
                    "action": "error",
                    "voice_url": None,
                    "error": str(e)
                }
        else:
            # 处理虚拟人动作指令
            if action_type:
                # 目前只有转圈和停止两个动作
                action_code = self.actions.get(action_type, "0")
                
                return {
                    "text": action_text,
                    "emotion": "happy" if action_type == "spin" else "neutral",
                    "action": action_type,
                    "action_code": action_code,
                    "voice_url": None
                }
            else:
                # 返回普通交互的模拟结果
                return {
                    "text": f"收到您的消息：{message}",
                    "emotion": "neutral",
                    "action": "listening",
                    "voice_url": None
                }
    
    def _format_available_humans(self, humans: List[Dict]) -> str:
        """
        格式化可用虚拟人列表
        
        Args:
            humans: 虚拟人列表
            
        Returns:
            格式化的文本
        """
        response_parts = ["以下是可以与您交互的虚拟人：\n"]
        
        for human in humans:
            name = human.get("name", "未知")
            personality = human.get("personality", "")
            specialties = human.get("specialties", [])
            
            response_parts.append(
                f"👤 **{name}**\n"
                f"   性格：{personality}\n"
                f"   擅长：{', '.join(specialties)}\n"
            )
        
        response_parts.append("\n您可以选择与任何一位虚拟人交流，只需说出他们的名字即可。")
        
        return "\n".join(response_parts)
    
    def _format_interaction_result(self, virtual_human_name: str, result: Dict) -> str:
        """
        格式化虚拟人交互结果
        
        Args:
            virtual_human_name: 虚拟人名称
            result: 交互结果
            
        Returns:
            格式化的响应
        """
        text = result.get("text", "")
        emotion = result.get("emotion", "neutral")
        action = result.get("action", "")
        error = result.get("error", None)
        
        # 如果有错误，返回错误信息
        if error:
            return f"【虚拟人交互失败】\n{text}"
        
        # 添加情感表情
        emotion_emojis = {
            "happy": "😊",
            "thinking": "🤔",
            "excited": "🎉",
            "sad": "😢",
            "neutral": "😐",
            "surprised": "😮",
            "error": "❌"
        }
        
        emoji = emotion_emojis.get(emotion, "")
        
        # 构建响应
        response = f"【{virtual_human_name}】{emoji}\n{text}"
        
        # 如果有动作描述
        if action:
            action_descriptions = {
                "greeting": "*友好地打招呼*",
                "explaining": "*认真地解释*",
                "creative": "*充满创意地表达*",
                "listening": "*专注地倾听*",
                "spin": "*开始转圈*",
                "stop": "*停止转圈*"
            }
            action_desc = action_descriptions.get(action, f"*{action}*")
            response = f"{action_desc}\n\n{response}"
            
            # 添加动作代码说明（如果有）
            if "action_code" in result:
                response += f"\n\n[动作代码: {result['action_code']}]"
        
        return response 
    
    def _detect_action_command(self, message: str) -> tuple[Optional[str], str]:
        """
        检测消息中是否包含虚拟人动作指令
        
        Args:
            message: 用户消息
            
        Returns:
            (动作类型, 响应文本)，如果没有检测到动作则动作类型为None
        """
        # 检查是否包含转圈指令
        for cmd in self.spin_commands:
            if cmd in message:
                return "spin", "好的，我开始转圈了！"
        
        # 检查是否包含停止指令
        for cmd in self.stop_commands:
            if cmd in message:
                return "stop", "好的，我停下来了。"
        
        # 没有检测到动作指令
        return None, "" 