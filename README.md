# 🤖 AI虚拟数字人项目

一个功能完整的AI虚拟数字人Web应用，集成3D VRM模型展示、智能对话系统和多种大模型支持。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-orange.svg)](https://threejs.org/)
[![VRM](https://img.shields.io/badge/VRM-0.6.11-purple.svg)](https://vrm.dev/)

## ✨ 功能特点

### 🎮 3D数字人展示
- **VRM模型支持**: 完整支持VRM格式数字人模型
- **实时3D渲染**: 基于Three.js的高性能WebGL渲染
- **智能相机控制**: 自适应模型尺寸的相机定位
- **流畅交互**: 优化的旋转、缩放、平移控制
- **响应式设计**: 完美适配桌面和移动设备

### 🧠 AI对话系统
- **多模型支持**: 集成OpenAI、Anthropic、DeepSeek等主流大模型
- **实时聊天**: 流畅的对话体验与数字人互动
- **智能切换**: 自动检测可用模型并智能切换
- **历史记录**: 完整的对话历史管理
- **错误处理**: 友好的错误提示和自动重试

### 🎨 用户界面
- **现代化设计**: 简洁美观的Material Design风格
- **暗色主题**: 护眼的深色界面设计
- **Toast提示**: 优雅的消息提示系统
- **加载动画**: 流畅的加载状态指示
- **快捷键支持**: 丰富的键盘快捷键操作

## 🏗️ 项目架构

```
virtual-human/
├── app.py                      # Flask应用入口
├── requirements.txt            # Python依赖包
├── config.env                  # 环境配置文件
├── README.md                   # 项目文档
│
├── app/                        # 应用核心模块
│   ├── __init__.py            # Flask应用初始化
│   ├── config.py              # 配置管理
│   ├── models.py              # AI模型接口
│   ├── routes.py              # 路由处理
│   │
│   ├── templates/             # HTML模板
│   │   └── index.html         # 主页面模板
│   │
│   └── static/                # 静态资源
│       ├── css/               # 样式文件
│       │   └── style.css      # 主样式
│       ├── js/                # JavaScript文件
│       │   └── app.js         # 主应用脚本
│       └── models/            # VRM模型文件
│           └── virtual-human.vrm
│
└── instance/                   # 实例配置
    └── config.py              # 本地配置
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd virtual-human

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

复制配置文件并根据需要修改：

```bash
cp config.env.example config.env
```

编辑 `config.env` 文件，配置您的AI模型API密钥：

```env
# 选择当前使用的提供商
CURRENT_PROVIDER=deepseek

# DeepSeek配置（推荐）
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# 或者配置其他提供商
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. 运行应用

```bash
python app.py
```

应用将在 http://localhost:8080 启动

## 🤖 AI模型配置

### 支持的模型提供商

| 提供商 | 模型 | 特点 |
|-------|------|------|
| **DeepSeek** | deepseek-chat, deepseek-coder | 高性价比，中英文优秀 |
| **OpenAI** | gpt-3.5-turbo, gpt-4 | 业界标杆，功能全面 |
| **Anthropic** | claude-3-haiku, claude-3-sonnet | 安全可靠，逻辑强 |
| **百度** | ernie-bot, ernie-bot-turbo | 中文优化 |
| **阿里** | qwen-turbo, qwen-plus | 国产化支持 |
| **腾讯** | hunyuan | 企业级服务 |
| **本地** | 自定义模型 | 私有部署 |

### DeepSeek配置指南

#### 获取API Key
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号并获取API Key

#### 配置步骤
```env
# 在config.env中设置
CURRENT_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_TEMPERATURE=0.7
```

#### 可用模型
- **deepseek-chat**: 通用对话模型，适合日常聊天
- **deepseek-coder**: 代码专用模型，编程任务优化

## 🎮 3D交互控制

### 🖱️ 鼠标操作

| 操作 | 功能 | 说明 |
|------|------|------|
| **左键拖拽** | 旋转视角 | 围绕数字人旋转观看角度 |
| **滚轮** | 缩放距离 | 拉近或拉远观看距离 |
| **右键拖拽** | 平移视角 | 上下左右移动观看位置 |

### ⌨️ 键盘快捷键

| 按键 | 功能 | 详细说明 |
|------|------|----------|
| **R** | 重置视角 | 将相机重置到最佳观看位置 |
| **A** | 自动旋转 | 开启/关闭自动旋转功能 |
| **空格** | 动画控制 | 暂停/播放数字人动画 |

### 🎯 操作技巧

#### 最佳观看体验
1. **初始加载**: 系统自动计算最佳相机位置
2. **视角迷失**: 按R键快速重置到理想视角
3. **观看细节**: 使用滚轮拉近观察数字人细节
4. **全方位观看**: 拖拽旋转360度无死角观看

#### 性能优化
- **渐进式阻尼**: 松开鼠标后视角平滑停止
- **角度保护**: 防止视角翻转到不自然角度
- **距离限制**: 合理的最近和最远观看距离
- **自适应渲染**: 根据设备性能调整渲染质量

## 💻 技术栈

### 后端技术
- **Python 3.7+**: 核心开发语言
- **Flask 2.0+**: 轻量级Web框架
- **Requests**: HTTP客户端库
- **Python-dotenv**: 环境变量管理

### 前端技术
- **Three.js r128**: 3D图形渲染引擎
- **VRM Loader 0.6.11**: VRM模型加载器
- **OrbitControls**: 3D场景交互控制
- **现代CSS3**: 响应式布局和动画
- **原生JavaScript**: 无框架依赖

### AI集成
- **OpenAI API**: GPT系列模型接口
- **Anthropic API**: Claude系列模型接口
- **DeepSeek API**: DeepSeek系列模型接口
- **多厂商兼容**: 统一的API调用接口

## 🎨 界面展示

```
┌─────────────────────────────────────────────────────────┐
│ 🤖 AI虚拟人 - Zy的家                    [提供商▼] [模型▼] │
├─────────────────────────────────────────────────────────┤
│                                               │ 💬 聊天 │
│           3D数字人展示区域                    ├─────────│
│        🖱️ 拖拽旋转 | R键重置                │ 对话区域 │
│                                               │         │
│                                               │ [输入框] │
└─────────────────────────────────────────────────────────┘
```

## 📱 浏览器兼容性

| 浏览器 | 最低版本 | WebGL支持 | 推荐 |
|--------|----------|-----------|------|
| Chrome | 60+ | ✅ | ⭐⭐⭐⭐⭐ |
| Firefox | 55+ | ✅ | ⭐⭐⭐⭐ |
| Safari | 12+ | ✅ | ⭐⭐⭐⭐ |
| Edge | 79+ | ✅ | ⭐⭐⭐⭐ |

**要求**: 浏览器必须支持WebGL 2.0

## 🔧 配置选项

### 环境变量配置

```env
# 基础配置
VIRTUAL_HUMAN_NAME=Zy        # 数字人名称
FLASK_HOST=0.0.0.0          # 服务器地址
FLASK_PORT=8080             # 服务端口
FLASK_DEBUG=False           # 调试模式

# AI模型配置
CURRENT_PROVIDER=deepseek   # 当前使用的提供商
DEFAULT_MODEL=deepseek-chat # 默认模型

# DeepSeek配置
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_TEMPERATURE=0.7

# OpenAI配置
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Anthropic配置
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-3-haiku-20240307
ANTHROPIC_MAX_TOKENS=2000
ANTHROPIC_TEMPERATURE=0.7
```

### VRM模型要求

- **格式**: VRM 0.0/1.0 标准格式
- **大小**: 建议不超过50MB（优化加载性能）
- **位置**: 放置在 `app/static/models/` 目录
- **命名**: 默认为 `virtual-human.vrm`

## 🛠️ 故障排除

### 常见问题

#### 模型加载失败
```
❌ 症状: 页面显示"模型加载失败"
🔧 解决方案:
  1. 检查VRM文件是否存在
  2. 验证文件是否损坏
  3. 确认文件格式正确
  4. 检查文件路径配置
```

#### AI对话无响应
```
❌ 症状: 发送消息后无回复
🔧 解决方案:
  1. 检查API密钥配置
  2. 验证网络连接
  3. 确认账户余额充足
  4. 查看浏览器控制台错误
```

#### 3D控制不流畅
```
❌ 症状: 旋转卡顿或无响应
🔧 解决方案:
  1. 按R键重置视角
  2. 检查浏览器性能
  3. 关闭其他占用资源的应用
  4. 尝试刷新页面
```

#### 网络连接问题
```
❌ 症状: CDN资源加载失败
🔧 解决方案:
  1. 检查网络连接
  2. 尝试使用VPN
  3. 下载本地化资源文件
  4. 配置代理服务器
```

### 调试技巧

1. **开启调试模式**: 设置 `FLASK_DEBUG=True`
2. **查看控制台**: 浏览器F12开发者工具
3. **检查网络**: 查看Network标签页请求状态
4. **测试API**: 使用Postman等工具测试API接口
5. **日志分析**: 查看Flask应用日志输出

## 🔄 版本更新

### 最新更新 (v2.0)
- ✨ 新增DeepSeek大模型支持
- 🎮 优化3D控制系统，提升交互体验
- ⌨️ 添加键盘快捷键支持
- 🎨 改进UI/UX设计，分离CSS和JS文件
- 🔧 重构代码架构，提升可维护性
- 📱 优化响应式设计
- 🚀 提升加载性能和稳定性

### 功能路线图
- [ ] 支持多种VRM模型切换
- [ ] 语音对话功能
- [ ] 表情和动作控制
- [ ] 自定义模型训练
- [ ] 移动端App版本
- [ ] 实时渲染优化

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 支持与反馈

- 🐛 **Bug报告**: [提交Issue](https://github.com/your-repo/issues)
- 💡 **功能建议**: [功能请求](https://github.com/your-repo/issues)
- 📧 **联系邮箱**: your-email@example.com
- 💬 **讨论社区**: [Discussions](https://github.com/your-repo/discussions)

## 🙏 致谢

- [Three.js](https://threejs.org/) - 强大的3D图形库
- [VRM](https://vrm.dev/) - 开放的虚拟形象标准
- [Flask](https://flask.palletsprojects.com/) - 简洁的Python Web框架
- [DeepSeek](https://platform.deepseek.com/) - 优秀的AI模型服务

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个Star！⭐**

Made with ❤️ by [Your Name]

</div> 