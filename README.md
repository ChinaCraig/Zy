# VRM数字人展示项目

这是一个简单的Python Flask web应用，用于在浏览器中展示VRM格式的数字人模型。

## 功能特点

- 🤖 支持VRM格式数字人模型展示
- 🎮 3D交互控制（鼠标拖拽旋转、滚轮缩放）
- 🎨 现代化美观的用户界面
- ⚡ 实时3D渲染
- 📱 响应式设计，支持移动端

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **3D渲染**: Three.js + VRM加载器
- **模型格式**: VRM (VRoid Studio导出)

## 项目结构

```
virtual-human/
├── app.py              # Flask主应用
├── requirements.txt    # Python依赖
├── templates/          # HTML模板
│   └── index.html      # 主页面
└── static/            # 静态资源
    └── models/        # VRM模型文件
        └── virtual-human.vrm
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:8080

## 使用说明

- **鼠标左键拖拽**: 旋转视角
- **鼠标滚轮**: 缩放视图
- **重置视角按钮**: 恢复默认相机位置
- **切换动画按钮**: 开启/关闭模型动画（如果有的话）

## 模型要求

- 支持VRM 0.0格式的模型文件
- 建议模型文件大小不超过50MB以获得最佳加载性能
- 模型文件需放置在`static/models/`目录下

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

需要浏览器支持WebGL 2.0功能。

## 故障排除

如果模型加载失败，请检查：
1. VRM文件是否在正确的目录下
2. 文件是否损坏
3. 浏览器是否支持WebGL
4. 网络连接是否正常（需要加载CDN资源） 