// 虚拟人聊天应用主脚本
// ================== 全局变量 ==================
let scene, camera, renderer, controls;
let vrmModel = null;
let mixer = null;
let clock = new THREE.Clock();
let isAnimating = false;
let currentProviders = [];
let isTyping = false;
let isIdentityVerified = false;
let userIdentity = null;
let chatTerminated = false;
let chatCount = 0;
let chatLimit = 100;

// ================== 3D场景初始化 ==================
function init() {
    // 创建场景
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x212121);
    
    // 创建相机
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1, 2);
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    
    document.getElementById('canvas-container').appendChild(renderer.domElement);
    
    // 相机控制
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1, 0);  // 看向数字人的胸部位置
    controls.enableDamping = true;
    controls.dampingFactor = 0.05; // 减少阻尼，使旋转更流畅
    controls.screenSpacePanning = false;
    controls.minDistance = 1.2;    // 最小距离稍微远一些
    controls.maxDistance = 8;      // 最大距离适中
    controls.maxPolarAngle = Math.PI * 0.9; // 允许更大的垂直旋转角度
    controls.minPolarAngle = Math.PI * 0.1; // 设置最小垂直角度，防止翻转
    controls.enablePan = true;     // 启用平移
    controls.panSpeed = 0.5;       // 平移速度
    controls.rotateSpeed = 0.8;    // 旋转速度
    controls.zoomSpeed = 1.0;      // 缩放速度
    controls.autoRotate = false;   // 关闭自动旋转
    controls.autoRotateSpeed = 2.0; // 自动旋转速度（如果需要启用）
    
    // 添加光照
    setupLights();
    
    // 加载VRM模型
    loadVRM();
    
    // 窗口大小调整
    window.addEventListener('resize', onWindowResize, false);
    
    // 添加键盘事件监听
    window.addEventListener('keydown', onKeyDown, false);
    
    // 开始渲染循环
    animate();
}

function setupLights() {
    // 主光源
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 1, 1).normalize();
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    
    // 环境光
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);
    
    // 补充光源
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-1, 0, -1).normalize();
    scene.add(fillLight);
}

function loadVRM() {
    const loader = new THREE.GLTFLoader();
    
    loader.load('/models/virtual-human.vrm', (gltf) => {
        THREE.VRM.from(gltf).then((vrm) => {
            vrmModel = vrm;
            scene.add(vrm.scene);
            
            // 隐藏加载提示
            document.getElementById('loading').style.display = 'none';
            
            // 设置模型位置和旋转
            vrm.scene.position.set(0, 0, 0);
            vrm.scene.rotation.set(0, 0, 0); // 确保模型正面朝向用户
            
            // 获取模型的边界框，用于更好的相机设置
            const box = new THREE.Box3().setFromObject(vrm.scene);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());
            
            // 调整相机位置以适配模型大小
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraDistance *= 1.5; // 增加一些缓冲距离
            
            // 更新相机位置
            camera.position.set(0, center.y, cameraDistance);
            camera.lookAt(center);
            
            // 更新控制器目标
            controls.target.copy(center);
            controls.update();
            
            // 如果有动画，创建混合器
            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(vrm.scene);
                const action = mixer.clipAction(gltf.animations[0]);
                action.play();
                isAnimating = true;
            }
            
            console.log('VRM模型加载成功！');
            console.log('模型尺寸:', size);
            console.log('模型中心:', center);
        });
    }, (progress) => {
        const percent = Math.round((progress.loaded / progress.total) * 100);
        document.querySelector('#loading p').textContent = `正在加载VRM模型... ${percent}%`;
    }, (error) => {
        console.error('VRM模型加载失败:', error);
        document.getElementById('loading').innerHTML = '<p>❌ 模型加载失败，请检查文件路径</p>';
    });
}

function animate() {
    requestAnimationFrame(animate);
    
    const deltaTime = clock.getDelta();
    
    // 更新控制器
    controls.update();
    
    // 更新VRM
    if (vrmModel) {
        vrmModel.update(deltaTime);
    }
    
    // 更新动画
    if (mixer && isAnimating) {
        mixer.update(deltaTime);
    }
    
    // 渲染
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    
    // 确保消息滚动到底部
    ensureMessageScroll();
}

function onKeyDown(event) {
    // 检查是否在输入框中输入，如果是则不处理快捷键
    const activeElement = document.activeElement;
    const isInputFocused = activeElement && (
        activeElement.tagName === 'INPUT' || 
        activeElement.tagName === 'TEXTAREA' || 
        activeElement.contentEditable === 'true'
    );
    
    if (isInputFocused) {
        return; // 输入框有焦点时不处理快捷键
    }
    
    switch (event.code) {
        case 'KeyR':
            // R键重置视角
            resetCameraView();
            break;
        case 'KeyA':
            // A键切换自动旋转
            toggleAutoRotate();
            break;
        case 'Space':
            // 空格键暂停/播放动画
            event.preventDefault();
            toggleAnimation();
            break;
    }
}

function resetCameraView() {
    if (vrmModel) {
        // 重置到默认视角
        const box = new THREE.Box3().setFromObject(vrmModel.scene);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = camera.fov * (Math.PI / 180);
        let cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        cameraDistance *= 1.5;
        
        // 平滑移动相机
        const targetPosition = new THREE.Vector3(0, center.y, cameraDistance);
        animateCameraTo(targetPosition, center);
        
        console.log('视角已重置');
        showInfo('视角已重置', '按R键重置视角');
    }
}

function toggleAutoRotate() {
    controls.autoRotate = !controls.autoRotate;
    const status = controls.autoRotate ? '开启' : '关闭';
    console.log(`自动旋转已${status}`);
    showInfo(`自动旋转已${status}`, '按A键切换自动旋转');
}

function toggleAnimation() {
    if (mixer && mixer._actions.length > 0) {
        const action = mixer._actions[0];
        if (action.paused) {
            action.paused = false;
            showInfo('动画已播放', '按空格键暂停/播放');
        } else {
            action.paused = true;
            showInfo('动画已暂停', '按空格键暂停/播放');
        }
    }
}

function animateCameraTo(targetPosition, targetLookAt) {
    const startPosition = camera.position.clone();
    const startTarget = controls.target.clone();
    
    let progress = 0;
    const duration = 1000; // 1秒
    const startTime = Date.now();
    
    function updateCamera() {
        progress = (Date.now() - startTime) / duration;
        if (progress >= 1) {
            progress = 1;
        }
        
        // 使用平滑插值
        const easeProgress = 1 - Math.pow(1 - progress, 3); // easeOut cubic
        
        camera.position.lerpVectors(startPosition, targetPosition, easeProgress);
        controls.target.lerpVectors(startTarget, targetLookAt, easeProgress);
        controls.update();
        
        if (progress < 1) {
            requestAnimationFrame(updateCamera);
        }
    }
    
    updateCamera();
}

// ================== 消息滚动功能 ==================
function ensureMessageScroll() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// ================== Toast消息提示功能 ==================
function showToast(message, type = 'info', title = '', duration = 4000) {
    const container = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();
    
    // 图标映射
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
        default: '🔔'
    };
    
    // 标题映射
    const titles = {
        success: title || '成功',
        error: title || '错误',
        warning: title || '警告',
        info: title || '提示',
        default: title || '通知'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.id = toastId;
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.default}</div>
        <div class="toast-content">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="closeToast('${toastId}')">×</button>
    `;
    
    container.appendChild(toast);
    
    // 显示动画
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // 自动关闭
    if (duration > 0) {
        setTimeout(() => {
            closeToast(toastId);
        }, duration);
    }
    
    return toastId;
}

function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// 便捷方法
function showSuccess(message, title, duration) {
    return showToast(message, 'success', title, duration);
}

function showError(message, title, duration) {
    return showToast(message, 'error', title, duration);
}

function showWarning(message, title, duration) {
    return showToast(message, 'warning', title, duration);
}

function showInfo(message, title, duration) {
    return showToast(message, 'info', title, duration);
}

// 确认对话框
function showConfirm(message, title = '确认', onConfirm, onCancel) {
    const container = document.getElementById('toast-container');
    const confirmId = 'confirm-' + Date.now();
    
    const confirmDialog = document.createElement('div');
    confirmDialog.className = 'toast warning';
    confirmDialog.id = confirmId;
    confirmDialog.style.maxWidth = '450px';
    
    confirmDialog.innerHTML = `
        <div class="toast-icon">❓</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
            <div style="display: flex; gap: 8px; margin-top: 12px;">
                <button onclick="handleConfirm('${confirmId}', true)" style="
                    background: #10b981;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 13px;
                    flex: 1;
                    transition: background 0.2s ease;
                " onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">确定</button>
                <button onclick="handleConfirm('${confirmId}', false)" style="
                    background: #f3f4f6;
                    color: #374151;
                    border: 1px solid #d1d5db;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 13px;
                    flex: 1;
                    transition: all 0.2s ease;
                " onmouseover="this.style.background='#e5e7eb'" onmouseout="this.style.background='#f3f4f6'">取消</button>
            </div>
        </div>
    `;
    
    // 存储回调函数
    window['confirm_' + confirmId] = { onConfirm, onCancel };
    
    container.appendChild(confirmDialog);
    
    // 显示动画
    setTimeout(() => {
        confirmDialog.classList.add('show');
    }, 100);
}

function handleConfirm(confirmId, result) {
    const callbacks = window['confirm_' + confirmId];
    
    if (result && callbacks.onConfirm) {
        callbacks.onConfirm();
    } else if (!result && callbacks.onCancel) {
        callbacks.onCancel();
    }
    
    // 清理
    delete window['confirm_' + confirmId];
    closeToast(confirmId);
}

// ================== 聊天功能 ==================
function initChat() {
    const chatForm = document.getElementById('chat-input-form');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    // 处理表单提交
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // 回车发送消息
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 检查身份验证状态
    checkIdentityStatus();
}

async function checkIdentityStatus() {
    try {
        const response = await fetch('/llm/identity_status');
        const data = await response.json();
        
        if (data.success) {
            isIdentityVerified = data.is_identity_verified;
            userIdentity = data.user_identity;
            chatTerminated = data.chat_terminated;
            chatCount = data.chat_count;
            chatLimit = data.chat_limit;
            
            // 更新聊天状态跟踪
            updateChatStatus(data);
            
            // 更新UI状态
            updateChatUI();
            
            // 如果需要身份验证且未验证，显示身份验证提示
            if (data.enable_identity_verification && !isIdentityVerified) {
                showIdentityPrompt(data.identity_prompt);
            }
            
            // 如果聊天已终止，显示终止提示
            if (chatTerminated) {
                showChatTerminatedMessage();
            }
        }
    } catch (error) {
        console.error('检查身份状态失败:', error);
    }
}

function updateChatUI() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    if (chatTerminated) {
        chatInput.disabled = true;
        sendButton.disabled = true;
        chatInput.placeholder = '聊天已达到上限，请清空历史后继续...';
    } else if (!isIdentityVerified) {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.placeholder = '请输入您的姓名或昵称进行身份确认...';
    } else {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.placeholder = `和 ${userIdentity || '我'} 聊天中...`;
    }
    
    // 更新聊天计数显示
    updateChatCounter();
}

function updateChatCounter() {
    // 在聊天标题中显示计数
    const chatTitle = document.querySelector('.chat-title span:last-child');
    if (chatTitle && chatLimit > 0) {
        const originalText = chatTitle.textContent.split(' (')[0]; // 移除之前的计数
        chatTitle.textContent = `${originalText} (${chatCount}/${chatLimit})`;
    }
}

function showIdentityPrompt(prompt) {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="message assistant">
            <div>${prompt}</div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;
}

function showChatTerminatedMessage() {
    const messagesContainer = document.getElementById('chat-messages');
    const terminatedMessage = document.createElement('div');
    terminatedMessage.className = 'message assistant';
    terminatedMessage.innerHTML = `
        <div>聊天已达到存储上限，请清空历史后继续对话。</div>
        <div class="message-time">${formatTime(new Date())}</div>
    `;
    messagesContainer.appendChild(terminatedMessage);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function setInitialTime() {
    const firstMessage = document.querySelector('.message-time');
    if (firstMessage) {
        firstMessage.textContent = formatTime(new Date());
    }
}

async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message || isTyping) return;
    
    // 检查聊天是否已终止
    if (chatTerminated) {
        showWarning('聊天已达到存储上限，请清空历史后继续对话。', '无法发送');
        return;
    }
    
    // 添加用户消息到界面
    addMessage(message, 'user');
    chatInput.value = '';
    
    // 显示输入状态
    showTyping();
    
    try {
        const response = await fetch('/llm/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        hideTyping();
        
        if (data.success) {
            addMessage(data.response, 'assistant');
            
            // 检查是否刚完成身份验证（通过检查欢迎消息）
            if (!isIdentityVerified && (data.response.includes('很高兴认识') || data.response.includes('很开心认识') || data.response.includes('好好听的名字'))) {
                isIdentityVerified = true;
                userIdentity = message;
                updateChatUI();
                // 重新获取身份状态以同步服务器状态
                setTimeout(checkIdentityStatus, 500);
                
                // 身份验证成功后才开始计数
                chatCount = 1;
            } else if (isIdentityVerified) {
                // 只有身份验证完成后才计数普通聊天
                chatCount++;
            }
            // 如果未验证身份且不是欢迎消息，说明是身份验证失败，不计数
            
            // 更新聊天状态跟踪
            updateChatStatus({
                chat_count: chatCount,
                user_identity: userIdentity,
                is_identity_verified: isIdentityVerified
            });
            
            updateChatCounter();
            
            // 检查是否达到聊天上限
            if (isIdentityVerified && chatCount >= chatLimit) {
                chatTerminated = true;
                updateChatUI();
            }
        } else {
            addMessage(data.error || '抱歉，我现在有点困惑 😅', 'assistant');
        }
    } catch (error) {
        hideTyping();
        console.error('发送消息错误:', error);
        addMessage('抱歉，网络连接出现问题 😅', 'assistant');
    }
}

function addMessage(content, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = formatTime(new Date());
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTyping() {
    isTyping = true;
    const typingIndicator = document.querySelector('.typing-indicator');
    const sendButton = document.getElementById('send-button');
    
    typingIndicator.style.display = 'block';
    sendButton.disabled = true;
    
    // 滚动到底部
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTyping() {
    isTyping = false;
    const typingIndicator = document.querySelector('.typing-indicator');
    const sendButton = document.getElementById('send-button');
    
    typingIndicator.style.display = 'none';
    sendButton.disabled = false;
}

function formatTime(date) {
    return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// ================== 模型配置功能 ==================
async function loadProviders() {
    try {
        const response = await fetch('/llm/providers');
        const data = await response.json();
        
        if (data.success) {
            currentProviders = data.providers;
            updateProviderSelect(data.current_provider, data.current_model);
        }
    } catch (error) {
        console.error('加载提供商失败:', error);
    }
}

function updateProviderSelect(currentProvider, currentModel) {
    const providerSelect = document.getElementById('provider-select');
    const modelSelect = document.getElementById('model-select');
    
    // 清空选项
    providerSelect.innerHTML = '<option value="">选择提供商...</option>';
    modelSelect.innerHTML = '<option value="">选择模型...</option>';
    
    // 添加提供商选项
    currentProviders.forEach(provider => {
        const option = document.createElement('option');
        option.value = provider.id;
        option.textContent = provider.name;
        if (provider.id === currentProvider) {
            option.selected = true;
        }
        providerSelect.appendChild(option);
    });
    
    // 监听提供商选择变化
    providerSelect.addEventListener('change', function() {
        updateModelSelect(this.value, currentModel);
        // 如果选择了提供商，自动切换
        if (this.value) {
            autoSwitchProvider();
        }
    });
    
    // 初始化模型选择
    if (currentProvider) {
        updateModelSelect(currentProvider, currentModel);
    }
}

function updateModelSelect(providerId, currentModel) {
    const modelSelect = document.getElementById('model-select');
    const provider = currentProviders.find(p => p.id === providerId);
    
    // 清空模型选项
    modelSelect.innerHTML = '<option value="">选择模型...</option>';
    
    if (provider && provider.models) {
        provider.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (model === currentModel) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
        
        // 监听模型选择变化
        modelSelect.addEventListener('change', function() {
            // 如果选择了模型，自动切换
            if (this.value) {
                autoSwitchProvider();
            }
        });
    }
}

// 自动切换提供商（不显示提示）
async function autoSwitchProvider() {
    const providerSelect = document.getElementById('provider-select');
    const modelSelect = document.getElementById('model-select');
    const provider = providerSelect.value;
    const model = modelSelect.value;
    
    if (!provider) {
        return;
    }
    
    try {
        const response = await fetch('/llm/switch_provider', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ provider, model })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 静默切换，不显示提示
            console.log('模型切换成功:', data.message);
        } else {
            console.error('切换失败:', data.error);
        }
    } catch (error) {
        console.error('切换提供商错误:', error);
    }
}

async function clearHistory() {
    // 使用自定义确认对话框
    showConfirm('确定要清空聊天历史吗？', '清空确认', () => {
        performClearHistory();
    });
}

async function performClearHistory() {
    try {
        const response = await fetch('/llm/clear_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                end_reason: 'user_clear'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 重置所有状态
            isIdentityVerified = false;
            userIdentity = null;
            chatTerminated = false;
            chatCount = 0;
            
            // 清除会话标记，下次刷新会重新检测
            sessionStorage.removeItem('virtual_human_session');
            
            // 更新UI状态
            updateChatUI();
            
            // 重新检查身份验证状态
            await checkIdentityStatus();
            
            showSuccess('聊天历史已清空', '操作完成');
        } else {
            showError(data.error, '清空失败');
        }
    } catch (error) {
        console.error('清空历史错误:', error);
        showError('网络连接出现问题，请稍后重试', '清空失败');
    }
}

// ================== 应用初始化 ==================
// 初始化应用
init();

// 检测浏览器刷新并自动清空历史
async function handlePageRefresh() {
    const sessionKey = 'virtual_human_session';
    const currentSession = sessionStorage.getItem(sessionKey);
    
    if (!currentSession) {
        // 检查服务器端是否有聊天记录
        try {
            const response = await fetch('/llm/identity_status');
            const status = await response.json();
            
            // 如果服务器有聊天记录或身份验证状态，说明是刷新页面
            if (status.success && (status.is_identity_verified || status.chat_count > 0)) {
                console.log('检测到页面刷新，准备归档并清空聊天历史');
                console.log('当前状态:', {
                    user_identity: status.user_identity,
                    chat_count: status.chat_count,
                    is_identity_verified: status.is_identity_verified
                });
                
                // 清空服务器端的历史并归档
                try {
                    const clearResponse = await fetch('/llm/clear_history', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            end_reason: 'browser_refresh'
                        })
                    });
                    
                    const clearResult = await clearResponse.json();
                    if (clearResult.success) {
                        console.log('页面刷新：聊天历史已归档并清空');
                        
                        // 重置前端状态和界面
                        isIdentityVerified = false;
                        userIdentity = null;
                        chatTerminated = false;
                        chatCount = 0;
                        
                        // 清空聊天消息界面
                        const messagesContainer = document.getElementById('chat-messages');
                        if (messagesContainer) {
                            messagesContainer.innerHTML = '';
                        }
                        
                        // 更新UI状态
                        updateChatUI();
                        
                        // 重新检查身份状态以显示身份验证提示
                        setTimeout(async () => {
                            await checkIdentityStatus();
                        }, 100);
                        
                        // 显示提示信息
                        if (typeof showInfo === 'function') {
                            if (status.is_identity_verified && status.chat_count > 0) {
                                showInfo(`${status.user_identity} 的聊天记录已保存，新会话开始`, '页面刷新检测');
                            } else {
                                showInfo('检测到页面刷新，聊天历史已清空', '新会话开始');
                            }
                        }
                    } else {
                        console.error('清空历史失败:', clearResult.error);
                    }
                } catch (clearError) {
                    console.error('清空历史请求失败:', clearError);
                }
            }
        } catch (error) {
            console.error('检查状态失败:', error);
        }
        
        // 标记当前会话
        sessionStorage.setItem(sessionKey, 'active');
    }
}

// 获取地理位置信息
async function getLocationInfo() {
    return new Promise((resolve) => {
        if (navigator.geolocation) {
            const options = {
                timeout: 5000,
                maximumAge: 300000, // 5分钟缓存
                enableHighAccuracy: false
            };
            
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    try {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        
                        // 可选：调用地理编码API获取城市信息
                        // 这里只返回坐标，避免依赖外部服务
                        resolve(`${lat.toFixed(4)},${lon.toFixed(4)}`);
                    } catch (error) {
                        console.warn('地理位置信息处理失败:', error);
                        resolve(null);
                    }
                },
                (error) => {
                    console.warn('无法获取地理位置:', error.message);
                    resolve(null);
                },
                options
            );
        } else {
            console.warn('浏览器不支持地理位置API');
            resolve(null);
        }
    });
}

// 设置会话信息
async function setSessionInfo() {
    try {
        const locationInfo = await getLocationInfo();
        
        const response = await fetch('/llm/set_session_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location_info: locationInfo
            })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('会话信息已设置:', data.session_info);
        }
    } catch (error) {
        console.warn('设置会话信息失败:', error);
    }
}

// 页面加载完成后初始化聊天功能
document.addEventListener('DOMContentLoaded', async function() {
    // 首先处理页面刷新逻辑
    await handlePageRefresh();
    
    // 设置会话信息
    await setSessionInfo();
    
    // 然后初始化聊天功能
    initChat();
    loadProviders();
    setInitialTime();
}); 

// 全局变量来跟踪当前聊天状态
let currentChatStatus = {
    hasChat: false,
    userIdentity: null,
    chatCount: 0
};

// 标志变量防止重复保存
let chatSaved = false;

// 定期更新聊天状态（每次发送消息后）
function updateChatStatus(status) {
    currentChatStatus = {
        hasChat: status.chat_count > 0,
        userIdentity: status.user_identity,
        chatCount: status.chat_count
    };
    // 重置保存标志，因为有新的聊天内容
    chatSaved = false;
}

// 保存聊天记录的统一函数
function saveChatHistory(reason) {
    // 检查是否有聊天记录需要保存且未保存过
    if (currentChatStatus.hasChat && currentChatStatus.userIdentity && !chatSaved) {
        console.log(`页面即将${reason === 'browser_unload' ? '关闭/刷新' : '隐藏'}，保存聊天记录...`);
        
        // 标记为已保存，防止重复保存
        chatSaved = true;
        
        // 使用 navigator.sendBeacon 保存数据（最可靠的方式）
        const saveData = JSON.stringify({
            end_reason: reason
        });
        
        if (navigator.sendBeacon) {
            const blob = new Blob([saveData], { type: 'application/json' });
            navigator.sendBeacon('/llm/clear_history', blob);
            console.log(`使用 sendBeacon 保存聊天记录 (${reason})`);
        } else {
            // 回退到同步 XMLHttpRequest（阻塞但可靠）
            try {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/llm/clear_history', false); // 同步请求
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(saveData);
                console.log(`使用同步 XHR 保存聊天记录 (${reason})`);
            } catch (error) {
                console.error('同步保存失败:', error);
            }
        }
    } else if (chatSaved) {
        console.log(`聊天记录已保存过，跳过重复保存 (${reason})`);
    }
}

// 监听页面关闭或刷新事件，确保保存聊天记录
window.addEventListener('beforeunload', function(event) {
    saveChatHistory('browser_unload');
});

// 也监听 pagehide 事件（移动端更可靠）
window.addEventListener('pagehide', function(event) {
    saveChatHistory('page_hide');
}); 