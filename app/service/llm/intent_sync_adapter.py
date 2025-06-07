"""
意图处理同步适配器
用于在同步环境（如Flask）中调用异步的意图处理器
"""
import asyncio
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading


class IntentSyncAdapter:
    """同步适配器"""
    
    def __init__(self):
        """初始化适配器"""
        self._loop = None
        self._thread = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._start_event_loop()
    
    def _start_event_loop(self):
        """在后台线程中启动事件循环"""
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            loop.run_forever()
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        
        # 等待事件循环启动
        while self._loop is None:
            import time
            time.sleep(0.01)
    
    def process_message_sync(
        self, 
        handler_manager,
        message: str, 
        context: Optional[Dict] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        同步方式处理消息
        
        Args:
            handler_manager: 意图处理器管理器
            message: 用户消息
            context: 上下文
            parallel: 是否并行处理
            
        Returns:
            处理结果
        """
        # 在事件循环中执行异步函数
        future = asyncio.run_coroutine_threadsafe(
            handler_manager.process_message(message, context, parallel),
            self._loop
        )
        
        try:
            # 等待结果，设置超时时间
            result = future.result(timeout=30)
            return result
        except asyncio.TimeoutError:
            return {
                "success": False,
                "response": "处理超时，请稍后重试。",
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"处理失败：{str(e)}",
                "error": str(e)
            }
    
    def cleanup(self):
        """清理资源"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=1)
        self._executor.shutdown(wait=False)


# 创建全局适配器实例
intent_sync_adapter = IntentSyncAdapter() 