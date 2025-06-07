# API路由映射文档

## 📋 **路由重构说明**

项目已按功能模块重新组织路由，分为三个主要模块：**大语言模型(LLM)**、**视觉模型(Vision)**、**语音模型(Speech)**。

## 🔄 **路由模块化结构**

### **大语言模型路由 (LLM)**

所有大语言模型相关功能已迁移到 `/llm/*` 路径下：

| 新路径 | 方法 | 功能说明 |
|--------|------|----------|
| `/llm/chat` | POST | 聊天对话接口 |
| `/llm/providers` | GET | 获取模型提供商 |
| `/llm/switch_provider` | POST | 切换模型提供商 |
| `/llm/chat_history` | GET | 获取聊天历史 |
| `/llm/clear_history` | POST | 清空聊天历史 |
| `/llm/identity_status` | GET | 获取身份验证状态 |
| `/llm/set_session_info` | POST | 设置会话信息 |
| `/llm/chat_archive/user/<id>` | GET | 获取用户聊天归档 |
| `/llm/chat_archive/session/<id>` | GET | 获取会话详情 |
| `/llm/generate` | POST | 文本生成接口（扩展预留） |
| `/llm/complete` | POST | 文本补全接口（扩展预留） |

### **视觉模型路由 (Vision)**

预留的视觉处理功能路径：

| 新路径 | 方法 | 功能说明 |
|--------|------|----------|
| `/vision/analyze` | POST | 图像分析接口 |
| `/vision/detect` | POST | 目标检测接口 |
| `/vision/recognize` | POST | 图像识别接口 |
| `/vision/generate` | POST | 图像生成接口 |

### **语音模型路由 (Speech)**

预留的语音处理功能路径：

| 新路径 | 方法 | 功能说明 |
|--------|------|----------|
| `/speech/recognize` | POST | 语音识别接口 |
| `/speech/synthesize` | POST | 语音合成接口 |
| `/speech/process` | POST | 语音处理接口 |
| `/speech/convert` | POST | 语音格式转换接口 |

### **通用路由 (Common)**

应用级通用功能保留在原路径：

| 路径 | 方法 | 功能说明 |
|------|------|----------|
| `/` | GET | 主页 |
| `/models/<filename>` | GET | VRM模型文件服务 |
| `/api/config` | GET | 获取应用配置 |
| `/api/database/test` | GET | 数据库连接测试 |

## 🏗️ **目录结构**

```
app/
├── routes/
│   ├── __init__.py          # 路由包初始化，导出所有蓝图
│   ├── routes.py            # 通用路由（主页、配置、数据库等）
│   ├── llm_routes.py        # 大语言模型路由（完整实现）
│   ├── vision_routes.py     # 视觉模型路由（预留框架）
│   └── speech_routes.py     # 语音模型路由（预留框架）
├── service/
│   ├── __init__.py          # 服务包初始化
│   ├── llm_service.py       # 大语言模型服务类
│   ├── vision_service.py    # 视觉模型服务类
│   └── speech_service.py    # 语音模型服务类
└── ...
```

## 📝 **使用说明**

1. **大语言模型功能**：使用 `/llm/*` 路径访问所有聊天、对话相关功能
2. **视觉功能**：使用 `/vision/*` 路径（待实现）
3. **语音功能**：使用 `/speech/*` 路径（待实现）
4. **通用功能**：继续使用 `/api/*` 和根路径

## 🔧 **服务层架构**

每个路由模块都有对应的服务类，负责具体的业务逻辑：

- `LLMService` - 处理大语言模型相关业务
- `VisionService` - 处理图像视觉相关业务  
- `SpeechService` - 处理语音音频相关业务

## 🚀 **扩展计划**

这种模块化架构为项目未来扩展提供了清晰的结构：

1. **大语言模型模块**：已完成基础功能迁移
2. **视觉模型模块**：预留接口，等待功能实现
3. **语音模型模块**：预留接口，等待功能实现 