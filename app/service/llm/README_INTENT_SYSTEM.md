# 意图识别系统说明文档

## 概述

本系统为大语言模型服务增加了意图识别功能，能够自动识别用户输入中的意图类型，并调用相应的处理器进行处理。系统支持多意图识别、并行处理、易于扩展等特性。

## 系统架构

```
app/service/llm/
├── intent_detection_service.py    # 意图识别服务（核心）
├── intent_handler_base.py         # 处理器基类
├── intent_handler_manager.py      # 处理器管理器
├── intent_sync_adapter.py         # 同步适配器（Flask兼容）
├── chat_handler.py               # 普通聊天处理器
├── kb_search_handler.py          # 知识库检索处理器
├── vector_search_handler.py      # 向量搜索处理器
├── mcp_call_handler.py           # MCP调用处理器
├── virtual_human_handler.py      # 虚拟人交互处理器
└── intent_example.py             # 使用示例
```

## 支持的意图类型

1. **CHAT** - 普通聊天
2. **KB_SEARCH** - 知识库检索
3. **VECTOR_SEARCH** - 向量库检索
4. **MCP_CALL** - MCP调用
5. **VIRTUAL_HUMAN** - 虚拟人交互

## 使用方法

### 1. 在聊天接口中启用意图识别

```python
# POST /llm/chat
{
    "message": "请帮我查询黄芪的功效，并跟虚拟人聊聊",
    "enable_intent_detection": true,   # 启用意图识别
    "parallel_intents": true          # 并行处理多个意图
}
```

### 2. 单独使用意图检测

```python
# POST /llm/intent/detect
{
    "message": "我想了解MCP的功能",
    "context": []  # 可选的对话历史
}
```

### 3. 查看可用的意图处理器

```python
# GET /llm/intent/handlers
```

## 扩展指南

### 1. 添加新的意图类型

```python
# 在 intent_detection_service.py 中
class IntentType(Enum):
    # ... 现有意图
    NEW_INTENT = "new_intent"  # 新增意图
```

### 2. 创建新的处理器

```python
from app.service.llm import IntentHandlerBase, Intent, IntentType

class NewIntentHandler(IntentHandlerBase):
    def can_handle(self, intent: Intent) -> bool:
        return intent.type == IntentType.NEW_INTENT
    
    async def handle(self, intent: Intent, message: str, context=None):
        # 实现处理逻辑
        return {
            "success": True,
            "response": "处理结果",
            "data": {},
            "need_continue": False
        }
```

### 3. 注册新处理器

```python
from app.service.llm import intent_handler_manager

# 创建并注册处理器
new_handler = NewIntentHandler()
intent_handler_manager.register_handler(IntentType.NEW_INTENT, new_handler)
```

### 4. 自定义意图识别规则

```python
from app.service.llm import intent_detector, IntentType

# 添加关键词
intent_detector.intent_keywords[IntentType.NEW_INTENT] = [
    "关键词1", "关键词2"
]

# 添加正则模式
intent_detector.intent_patterns[IntentType.NEW_INTENT] = [
    r"正则表达式模式"
]
```

## 特性说明

### 1. 多意图识别
系统可以从一条消息中识别出多个意图，例如：
- "查询天气并翻译成英文" → [MCP_CALL, MCP_CALL]
- "查询黄芪功效并与虚拟人讨论" → [KB_SEARCH, VIRTUAL_HUMAN]

### 2. 并行处理
当识别到多个意图时，系统支持并行处理以提高效率。通过 `parallel_intents` 参数控制。

### 3. 上下文感知
意图识别会考虑对话历史，能够理解"这个"、"它"等指代词。

### 4. 置信度评分
每个识别出的意图都有置信度分数（0-1），系统会按置信度排序。

### 5. 优雅降级
如果意图处理失败，系统会自动回退到普通聊天模式。

## API 响应格式

### 启用意图识别的聊天响应

```json
{
    "success": true,
    "response": "合并的响应内容",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "virtual_human_name": "小爱",
    "intent_detection": true,
    "intents": [
        {
            "type": "kb_search",
            "confidence": 0.9,
            "params": {
                "search_terms": ["黄芪", "功效"]
            }
        }
    ],
    "intent_data": {
        "intent_0": {
            "results_count": 2,
            "results": [...]
        }
    }
}
```

### 意图检测响应

```json
{
    "success": true,
    "message": "原始消息",
    "intents": [
        {
            "type": "kb_search",
            "confidence": 0.9,
            "params": {}
        }
    ]
}
```

## 注意事项

1. **性能考虑**：并行处理多个意图时要注意资源消耗
2. **异步处理**：处理器使用异步方法，通过同步适配器在Flask中使用
3. **错误处理**：每个处理器都应该有完善的错误处理
4. **日志记录**：建议为每个处理器添加日志记录
5. **超时控制**：同步适配器设置了30秒的超时时间

## 后续优化建议

1. **使用 AI 模型进行意图识别**：当前使用规则匹配，可以升级为使用专门的意图分类模型
2. **添加意图优先级**：某些意图可能需要优先处理
3. **添加意图冲突解决**：当多个意图冲突时的处理策略
4. **性能监控**：添加意图识别和处理的性能指标
5. **缓存机制**：对频繁的意图识别结果进行缓存 