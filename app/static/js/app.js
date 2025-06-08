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

// ================== 骨骼控制系统 ==================
let availableBones = [];
let boneControlActive = false;
let actionSequence = []; // 动作序列
let selectedBone = null; // 当前选中的骨骼

// ================== VRM模型配置 ==================
const VRM_CONFIG = {
    // 初始旋转角度（弧度）- 调整这里可以改变人物朝向
    initialRotation: {
        x: 0,
        y: Math.PI, // Y轴旋转180度，让人物正面朝向用户
        z: 0
    }
};

// 骨骼中英文映射
const boneNameMap = {
    // 头部
    'head': '头部',
    'neck': '颈部', 
    'leftEye': '左眼',
    'rightEye': '右眼',
    'jaw': '下颌',
    
    // 躯干
    'hips': '臀部',
    'spine': '脊柱',
    'chest': '胸部',
    'upperChest': '上胸部',
    
    // 左臂
    'leftShoulder': '左肩',
    'leftUpperArm': '左上臂',
    'leftLowerArm': '左前臂',
    'leftHand': '左手',
    
    // 右臂
    'rightShoulder': '右肩',
    'rightUpperArm': '右上臂', 
    'rightLowerArm': '右前臂',
    'rightHand': '右手',
    
    // 左腿
    'leftUpperLeg': '左大腿',
    'leftLowerLeg': '左小腿',
    'leftFoot': '左脚',
    'leftToes': '左脚趾',
    
    // 右腿
    'rightUpperLeg': '右大腿',
    'rightLowerLeg': '右小腿',
    'rightFoot': '右脚',
    'rightToes': '右脚趾',
    
    // 左手指 - 详细映射
    'leftThumb1': '左拇指近端',
    'leftThumb2': '左拇指中端',
    'leftThumb3': '左拇指远端',
    'leftThumbProximal': '左拇指近节',
    'leftThumbIntermediate': '左拇指中节',
    'leftThumbDistal': '左拇指末节',
    
    'leftIndex1': '左食指近端',
    'leftIndex2': '左食指中端',
    'leftIndex3': '左食指远端',
    'leftIndexProximal': '左食指近节',
    'leftIndexIntermediate': '左食指中节',
    'leftIndexDistal': '左食指末节',
    
    'leftMiddle1': '左中指近端',
    'leftMiddle2': '左中指中端',
    'leftMiddle3': '左中指远端',
    'leftMiddleProximal': '左中指近节',
    'leftMiddleIntermediate': '左中指中节',
    'leftMiddleDistal': '左中指末节',
    
    'leftRing1': '左无名指近端',
    'leftRing2': '左无名指中端',
    'leftRing3': '左无名指远端',
    'leftRingProximal': '左无名指近节',
    'leftRingIntermediate': '左无名指中节',
    'leftRingDistal': '左无名指末节',
    
    'leftLittle1': '左小指近端',
    'leftLittle2': '左小指中端',
    'leftLittle3': '左小指远端',
    'leftLittleProximal': '左小指近节',
    'leftLittleIntermediate': '左小指中节',
    'leftLittleDistal': '左小指末节',
    
    // 右手指 - 详细映射
    'rightThumb1': '右拇指近端',
    'rightThumb2': '右拇指中端',
    'rightThumb3': '右拇指远端',
    'rightThumbProximal': '右拇指近节',
    'rightThumbIntermediate': '右拇指中节',
    'rightThumbDistal': '右拇指末节',
    
    'rightIndex1': '右食指近端',
    'rightIndex2': '右食指中端',
    'rightIndex3': '右食指远端',
    'rightIndexProximal': '右食指近节',
    'rightIndexIntermediate': '右食指中节',
    'rightIndexDistal': '右食指末节',
    
    'rightMiddle1': '右中指近端',
    'rightMiddle2': '右中指中端',
    'rightMiddle3': '右中指远端',
    'rightMiddleProximal': '右中指近节',
    'rightMiddleIntermediate': '右中指中节',
    'rightMiddleDistal': '右中指末节',
    
    'rightRing1': '右无名指近端',
    'rightRing2': '右无名指中端',
    'rightRing3': '右无名指远端',
    'rightRingProximal': '右无名指近节',
    'rightRingIntermediate': '右无名指中节',
    'rightRingDistal': '右无名指末节',
    
    'rightLittle1': '右小指近端',
    'rightLittle2': '右小指中端',
    'rightLittle3': '右小指远端',
    'rightLittleProximal': '右小指近节',
    'rightLittleIntermediate': '右小指中节',
    'rightLittleDistal': '右小指末节'
};

// 获取骨骼中文名称
function getChineseBoneName(englishName) {
    return boneNameMap[englishName] || englishName;
}

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
            window.currentVRM = vrm; // 同时设置全局变量供其他功能使用
            scene.add(vrm.scene);
            
            // 隐藏加载提示
            document.getElementById('loading').style.display = 'none';
            
            // 设置模型位置和旋转
            vrm.scene.position.set(0, 0, 0);
            // 使用配置中的旋转值，确保人物正面朝向用户
            vrm.scene.rotation.set(
                VRM_CONFIG.initialRotation.x,
                VRM_CONFIG.initialRotation.y,
                VRM_CONFIG.initialRotation.z
            );
            
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
            
            // 显示加载成功提示
            showSuccess('VRM模型加载成功！', '模型已就绪');
            
            // 更新状态指示器
            updateVRMStatus('ready', '✅', 'VRM模型已就绪');
            
            // 初始化骨骼控制系统
            initBoneControl();
        });
    }, (progress) => {
        const percent = Math.round((progress.loaded / progress.total) * 100);
        document.querySelector('#loading p').textContent = `正在加载VRM模型... ${percent}%`;
    }, (error) => {
        console.error('VRM模型加载失败:', error);
        document.getElementById('loading').innerHTML = '<p>❌ 模型加载失败，请检查文件路径</p>';
        
        // 更新状态指示器
        updateVRMStatus('error', '❌', 'VRM模型加载失败');
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

// ================== 虚拟人动作处理 ==================
function handleVirtualHumanAction(actionData) {
    if (!actionData) {
        console.warn('没有动作数据');
        return;
    }
    
    console.log('处理虚拟人动作:', actionData);
    
    const { action, action_code } = actionData;
    
    switch(action) {
        case 'spin':
            // 开始转圈动画
            controls.autoRotate = true;
            controls.autoRotateSpeed = 2.0;
            console.log('虚拟人开始转圈');
            showInfo('虚拟人开始转圈', '说"停下"可以停止');
            break;
            
        case 'stop':
            // 停止转圈动画
            controls.autoRotate = false;
            console.log('虚拟人停止转圈');
            showInfo('虚拟人停止转圈', '说"转圈"可以重新开始');
            break;
            
        default:
            console.log(`未知的动作类型: ${action}`);
            break;
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
    
    // 首先检查是否是骨骼控制指令
    if (boneControlActive && processBoneCommand(message)) {
        // 如果是骨骼控制指令，添加用户消息但不发送给AI
        addMessage(message, 'user');
        chatInput.value = '';
        return;
    }
    
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
            
            // 处理虚拟人动作（如果有）
            if (data.intent_detection && data.intent_data && data.intent_data.action) {
                handleVirtualHumanAction(data.intent_data.action);
            }
            
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

// ================== 骨骼控制系统 ==================
// 设置虚拟人初始姿势
function setInitialPose() {
    if (!vrmModel || !vrmModel.humanoid) {
        console.warn('VRM模型不可用，无法设置初始姿势');
        return;
    }
    
    console.log('设置虚拟人初始姿势...');
    
    // 双手自然垂下的角度设置（模拟人自然站立姿势）
    const naturalPose = {
        // 左臂自然垂下
        leftUpperArm: { x: 0, y: 0, z: Math.PI / 6 },     // 左上臂向下30度
        leftLowerArm: { x: -Math.PI / 12, y: 0, z: 0 },   // 左前臂稍微弯曲15度
        leftHand: { x: 0, y: 0, z: 0 },                   // 左手自然状态
        
        // 右臂自然垂下  
        rightUpperArm: { x: 0, y: 0, z: -Math.PI / 6 },   // 右上臂向下30度
        rightLowerArm: { x: -Math.PI / 12, y: 0, z: 0 },  // 右前臂稍微弯曲15度
        rightHand: { x: 0, y: 0, z: 0 },                  // 右手自然状态
        
        // 肩膀自然状态
        leftShoulder: { x: 0, y: 0, z: 0 },               // 左肩
        rightShoulder: { x: 0, y: 0, z: 0 },              // 右肩
    };
    
    // 应用初始姿势
    let setPoseCount = 0;
    for (const boneName in naturalPose) {
        try {
            const boneNode = vrmModel.humanoid.getBoneNode(boneName);
            if (boneNode) {
                const pose = naturalPose[boneName];
                
                // 保存原始旋转
                if (!boneNode.userData) {
                    boneNode.userData = {};
                }
                if (!boneNode.userData.originalRotation) {
                    boneNode.userData.originalRotation = {
                        x: boneNode.rotation.x,
                        y: boneNode.rotation.y,
                        z: boneNode.rotation.z
                    };
                }
                
                // 设置自然姿势
                boneNode.rotation.set(pose.x, pose.y, pose.z);
                setPoseCount++;
                
                console.log(`设置 ${boneName} 为自然姿势`);
            }
        } catch (error) {
            console.warn(`设置骨骼 ${boneName} 姿势失败:`, error);
        }
    }
    
    console.log(`初始姿势设置完成，共设置 ${setPoseCount} 个骨骼`);
}

// 初始化骨骼控制系统
function initBoneControl() {
    if (!vrmModel || !vrmModel.humanoid) {
        console.warn('VRM模型或humanoid不可用，无法初始化骨骼控制');
        return;
    }
    
    // 确保全局变量也设置正确
    window.currentVRM = vrmModel;
    
    // 获取所有可用的骨骼名称
    availableBones = [];
    console.log('=== Three-VRM 版本: 0.6.11 ===');
    console.log('=== 可用骨骼列表 ===');
    
    for (const name in vrmModel.humanoid.humanBones) {
        console.log(name);  // 打印每个支持的骨骼名称
        availableBones.push(name);
    }
    
    console.log(`总计 ${availableBones.length} 个骨骼可用`);
    
    // 激活骨骼控制
    boneControlActive = true;
    
    // 设置初始姿势（双手自然垂下）
    setInitialPose();
    
    // 显示骨骼控制提示
    showInfo(`骨骼控制系统已激活，共发现 ${availableBones.length} 个可控制骨骼`, '骨骼系统初始化');
    
    // 初始化骨骼控制面板
    initBoneControlPanel();
    
    // 检查移动端并显示相应控件
    checkMobileAndShowControls();
    
    // 为用户显示一些基本的骨骼控制指令示例
    setTimeout(() => {
        addMessage(`🦴 骨骼控制系统已激活！\n\n你可以使用以下基本指令控制我的骨骼：\n• "头向下" - 头部向下旋转30度\n• "头向左" / "头向右" - 头部左右旋转\n• "右上臂抬起" - 右上臂抬起60度\n• "右前臂弯曲" - 右前臂弯曲45度\n• "脊柱前倾" - 脊柱向前倾斜\n• "重置头部" / "重置右臂" - 重置特定部位\n• "重置" - 重置所有骨骼\n• "显示骨骼" - 查看所有可用骨骼\n\n💡 左侧有图形化骨骼控制面板可供使用！`, 'assistant');
    }, 1000);
}

// 重置特定骨骼到初始位置
function resetBone(boneName) {
    if (!vrmModel || !vrmModel.humanoid || !boneControlActive) {
        return false;
    }
    
    try {
        const boneNode = vrmModel.humanoid.getBoneNode(boneName);
        if (!boneNode) {
            console.warn(`骨骼 ${boneName} 不存在或不可用`);
            return false;
        }
        
        // 重置到原始旋转
        if (boneNode.userData && boneNode.userData.originalRotation) {
            boneNode.rotation.x = boneNode.userData.originalRotation.x;
            boneNode.rotation.y = boneNode.userData.originalRotation.y;
            boneNode.rotation.z = boneNode.userData.originalRotation.z;
        } else {
            // 如果没有保存原始旋转，重置为0
            boneNode.rotation.set(0, 0, 0);
        }
        
        console.log(`骨骼 ${boneName} 已重置`);
        return true;
    } catch (error) {
        console.error(`重置骨骼 ${boneName} 失败:`, error);
        return false;
    }
}

// 重置所有骨骼到初始位置
function resetAllBones() {
    if (!vrmModel || !vrmModel.humanoid || !boneControlActive) {
        return false;
    }
    
    try {
        let resetCount = 0;
        for (const name in vrmModel.humanoid.humanBones) {
            if (resetBone(name)) {
                resetCount++;
            }
        }
        console.log(`已重置 ${resetCount} 个骨骼`);
        return true;
    } catch (error) {
        console.error('重置所有骨骼失败:', error);
        return false;
    }
}

// 控制特定骨骼的旋转
function rotateBone(boneName, rotationX = 0, rotationY = 0, rotationZ = 0, duration = 1000) {
    if (!vrmModel || !vrmModel.humanoid || !boneControlActive) {
        return false;
    }
    
    try {
        // 使用正确的API获取骨骼节点  
        const boneNode = vrmModel.humanoid.getBoneNode(boneName);
        if (!boneNode) {
            console.warn(`骨骼 ${boneName} 不存在或不可用`);
            return false;
        }
        
        // 保存原始旋转（如果还没保存的话）
        if (!boneNode.userData) {
            boneNode.userData = {};
        }
        if (!boneNode.userData.originalRotation) {
            boneNode.userData.originalRotation = {
                x: boneNode.rotation.x,
                y: boneNode.rotation.y,
                z: boneNode.rotation.z
            };
        }
        
        // 直接设置旋转（弧度）
        boneNode.rotation.x = rotationX;
        boneNode.rotation.y = rotationY;  
        boneNode.rotation.z = rotationZ;
        
        console.log(`骨骼 ${boneName} 旋转设置: X=${rotationX.toFixed(2)}, Y=${rotationY.toFixed(2)}, Z=${rotationZ.toFixed(2)}`);
        return true;
    } catch (error) {
        console.error(`控制骨骼 ${boneName} 失败:`, error);
        return false;
    }
}

// 解析聊天指令并执行骨骼动作
function processBoneCommand(message) {
    if (!boneControlActive) {
        return false;
    }
    
    const lowerMessage = message.toLowerCase().trim();
    let actionPerformed = false;
    
    // 重置动作
    if (lowerMessage.includes('重置') || lowerMessage.includes('复位') || lowerMessage.includes('初始')) {
        if (resetAllBones()) {
            actionPerformed = true;
            setTimeout(() => {
                addMessage('✅ 所有骨骼已重置到初始位置', 'assistant');
            }, 100);
        }
    }
    
    // 头部简单旋转
    else if (lowerMessage.includes('头向下') || lowerMessage.includes('低头')) {
        if (rotateBone('head', Math.PI / 6, 0, 0)) { // 30度
            actionPerformed = true;
            addMessage('✅ 头部向下旋转30度', 'assistant');
        }
    }
    else if (lowerMessage.includes('头向左') || lowerMessage.includes('头左转')) {
        if (rotateBone('head', 0, -Math.PI / 6, 0)) { // -30度
            actionPerformed = true;
            addMessage('✅ 头部向左旋转30度', 'assistant');
        }
    }
    else if (lowerMessage.includes('头向右') || lowerMessage.includes('头右转')) {
        if (rotateBone('head', 0, Math.PI / 6, 0)) { // 30度
            actionPerformed = true;
            addMessage('✅ 头部向右旋转30度', 'assistant');
        }
    }
    
    // 右臂控制
    else if (lowerMessage.includes('右上臂') && lowerMessage.includes('抬起')) {
        if (rotateBone('rightUpperArm', 0, 0, -Math.PI / 3)) { // -60度
            actionPerformed = true;
            addMessage('✅ 右上臂已抬起60度', 'assistant');
        }
    }
    else if (lowerMessage.includes('左上臂') && lowerMessage.includes('抬起')) {
        if (rotateBone('leftUpperArm', 0, 0, Math.PI / 3)) { // 60度
            actionPerformed = true;
            addMessage('✅ 左上臂已抬起60度', 'assistant');
        }
    }
    
    // 前臂控制
    else if (lowerMessage.includes('右前臂') && lowerMessage.includes('弯曲')) {
        if (rotateBone('rightLowerArm', -Math.PI / 4, 0, 0)) { // -45度
            actionPerformed = true;
            addMessage('✅ 右前臂已弯曲45度', 'assistant');
        }
    }
    else if (lowerMessage.includes('左前臂') && lowerMessage.includes('弯曲')) {
        if (rotateBone('leftLowerArm', -Math.PI / 4, 0, 0)) { // -45度
            actionPerformed = true;
            addMessage('✅ 左前臂已弯曲45度', 'assistant');
        }
    }
    
    // 脊柱控制
    else if (lowerMessage.includes('脊柱') && lowerMessage.includes('前倾')) {
        if (rotateBone('spine', Math.PI / 6, 0, 0)) { // 30度
            actionPerformed = true;
            addMessage('✅ 脊柱向前倾斜30度', 'assistant');
        }
    }
    
    // 重置特定骨骼
    else if (lowerMessage.includes('重置头部')) {
        if (resetBone('head')) {
            actionPerformed = true;
            addMessage('✅ 头部已重置', 'assistant');
        }
    }
    else if (lowerMessage.includes('重置右臂')) {
        if (resetBone('rightUpperArm') && resetBone('rightLowerArm')) {
            actionPerformed = true;
            addMessage('✅ 右臂已重置', 'assistant');
        }
    }
    else if (lowerMessage.includes('重置左臂')) {
        if (resetBone('leftUpperArm') && resetBone('leftLowerArm')) {
            actionPerformed = true;
            addMessage('✅ 左臂已重置', 'assistant');
        }
    }
    
    // 显示可用骨骼
    else if (lowerMessage.includes('显示骨骼') || lowerMessage.includes('骨骼列表') || lowerMessage.includes('有哪些骨骼')) {
        actionPerformed = true;
        const boneList = availableBones.join('、');
        addMessage(`🦴 我当前有 ${availableBones.length} 个可控制的骨骼：\n\n${boneList}\n\n你可以尝试以下指令：\n• "头向下" - 头部向下30度\n• "右上臂抬起" - 右上臂抬起60度\n• "右前臂弯曲" - 右前臂弯曲45度\n• "重置头部" - 重置头部位置\n• "重置" - 重置所有骨骼`, 'assistant');
    }
    
    return actionPerformed;
}

// 修改原有的 sendMessage 函数，添加骨骼控制检查
const originalSendMessage = sendMessage;
window.sendMessage = async function() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 首先检查是否是骨骼控制指令
    if (boneControlActive && processBoneCommand(message)) {
        // 如果是骨骼控制指令，添加用户消息但不发送给AI
        addMessage(message, 'user');
        input.value = '';
        return;
    }
    
    // 否则执行原有的发送逻辑
    return originalSendMessage();
};

// ================== 骨骼控制面板 ==================
// 初始化骨骼控制面板
function initBoneControlPanel() {
    const panel = document.getElementById('bone-control-panel');
    if (panel) {
        panel.style.display = 'flex';
        console.log('骨骼控制面板已显示');
    } else {
        console.error('找不到骨骼控制面板元素');
    }
    
    // 创建骨骼列表
    createBoneList();
    
    // 初始化选择显示
    updateSelectionDisplay();
}

// 创建骨骼列表UI
function createBoneList() {
    const boneListContainer = document.getElementById('bone-list-panel');
    if (!boneListContainer || !availableBones.length) {
        return;
    }
    
    boneListContainer.innerHTML = '';
    
    // 按类别分组骨骼
    const boneCategories = {
        '头部区域': ['head', 'neck', 'leftEye', 'rightEye', 'jaw'],
        '躯干区域': ['hips', 'spine', 'chest', 'upperChest'],
        '左臂区域': ['leftShoulder', 'leftUpperArm', 'leftLowerArm', 'leftHand'],
        '右臂区域': ['rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand'],
        '左腿区域': ['leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'leftToes'],
        '右腿区域': ['rightUpperLeg', 'rightLowerLeg', 'rightFoot', 'rightToes'],
        '左手指区域': availableBones.filter(bone => bone.startsWith('left') && (bone.includes('Thumb') || bone.includes('Index') || bone.includes('Middle') || bone.includes('Ring') || bone.includes('Little'))),
        '右手指区域': availableBones.filter(bone => bone.startsWith('right') && (bone.includes('Thumb') || bone.includes('Index') || bone.includes('Middle') || bone.includes('Ring') || bone.includes('Little')))
    };
    
    Object.entries(boneCategories).forEach(([category, bones]) => {
        const availableBonesInCategory = bones.filter(bone => availableBones.includes(bone));
        
        if (availableBonesInCategory.length > 0) {
            // 创建分类标题
            const categoryElement = document.createElement('div');
            categoryElement.className = 'bone-category';
            categoryElement.innerHTML = `
                <div class="category-header">
                    <h4>${category} (${availableBonesInCategory.length})</h4>
                </div>
                <div class="category-bones"></div>
            `;
            
            const categoryBones = categoryElement.querySelector('.category-bones');
            
            // 为每个骨骼创建控制项
            availableBonesInCategory.forEach(boneName => {
                const boneItem = createBoneItem(boneName);
                categoryBones.appendChild(boneItem);
            });
            
            boneListContainer.appendChild(categoryElement);
        }
    });
    
    // 添加未分类的骨骼
    const uncategorizedBones = availableBones.filter(bone => 
        !Object.values(boneCategories).flat().includes(bone)
    );
    
    if (uncategorizedBones.length > 0) {
        const categoryElement = document.createElement('div');
        categoryElement.className = 'bone-category';
        categoryElement.innerHTML = `
            <div class="category-header">
                <h4>其他区域 (${uncategorizedBones.length})</h4>
            </div>
            <div class="category-bones"></div>
        `;
        
        const categoryBones = categoryElement.querySelector('.category-bones');
        uncategorizedBones.forEach(boneName => {
            const boneItem = createBoneItem(boneName);
            categoryBones.appendChild(boneItem);
        });
        
        boneListContainer.appendChild(categoryElement);
    }
}

// 创建单个骨骼控制项
function createBoneItem(boneName) {
    const chineseName = getChineseBoneName(boneName);
    const boneItem = document.createElement('div');
    boneItem.className = 'bone-item';
    boneItem.dataset.boneName = boneName;
    boneItem.innerHTML = `
        <div class="bone-header" onclick="selectBone('${boneName}')">
            <span class="bone-name" title="${boneName}">${chineseName}</span>
            <div class="bone-controls" onclick="event.stopPropagation()">
                <button class="bone-btn rotate" onclick="rotateBoneFromPanel('${boneName}')">旋转</button>
                <button class="bone-btn reset" onclick="resetBoneFromPanel('${boneName}')">重置</button>
            </div>
        </div>
    `;
    return boneItem;
}

// 从面板旋转骨骼
function rotateBoneFromPanel(boneName) {
    const rotX = parseFloat(document.getElementById('rotate-x').value) || 0;
    const rotY = parseFloat(document.getElementById('rotate-y').value) || 0;
    const rotZ = parseFloat(document.getElementById('rotate-z').value) || 0;
    
    // 转换为弧度
    const radX = (rotX * Math.PI) / 180;
    const radY = (rotY * Math.PI) / 180;
    const radZ = (rotZ * Math.PI) / 180;
    
    const chineseName = getChineseBoneName(boneName);
    
    if (rotateBone(boneName, radX, radY, radZ)) {
        showInfo(`${chineseName} 已旋转: X=${rotX}°, Y=${rotY}°, Z=${rotZ}°`, '骨骼控制');
    } else {
        showError(`无法旋转 ${chineseName}`, '控制失败');
    }
}

// 从面板重置骨骼
function resetBoneFromPanel(boneName) {
    const chineseName = getChineseBoneName(boneName);
    
    if (resetBone(boneName)) {
        showInfo(`${chineseName} 已重置`, '骨骼重置');
    } else {
        showError(`无法重置 ${chineseName}`, '重置失败');
    }
}

// 切换面板显示/隐藏
function toggleBonePanel() {
    const panel = document.getElementById('bone-control-panel');
    const content = document.getElementById('panel-content');
    const toggle = document.querySelector('.panel-toggle');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.textContent = '−';
        panel.style.width = '320px';
    } else {
        content.style.display = 'none';
        toggle.textContent = '+';
        panel.style.width = '60px';
    }
}

// 移动端切换骨骼面板
function toggleMobileBonePanel() {
    const panel = document.getElementById('bone-control-panel');
    if (panel) {
        panel.classList.toggle('mobile-show');
    }
}

// 检查是否为移动设备并显示相应控件
function checkMobileAndShowControls() {
    const isMobile = window.innerWidth <= 768;
    const mobileToggle = document.querySelector('.mobile-bone-toggle');
    
    if (mobileToggle) {
        mobileToggle.style.display = isMobile ? 'block' : 'none';
    }
}

// 监听窗口大小变化
window.addEventListener('resize', checkMobileAndShowControls);

// ================== 动作编排系统 ==================

// 选中骨骼
function selectBone(boneName) {
    // 移除之前的选中状态
    document.querySelectorAll('.bone-item.selected').forEach(item => {
        item.classList.remove('selected');
    });
    
    // 设置新的选中状态
    const boneItem = document.querySelector(`[data-bone-name="${boneName}"]`);
    if (boneItem) {
        boneItem.classList.add('selected');
    }
    
    selectedBone = boneName;
    updateSelectionDisplay();
    
    const chineseName = getChineseBoneName(boneName);
    showInfo(`已选中: ${chineseName}`, '骨骼选择');
}

// 更新选中显示
function updateSelectionDisplay() {
    const selectedBoneSpan = document.getElementById('selected-bone');
    const addButton = document.getElementById('add-to-sequence');
    
    if (selectedBone) {
        const chineseName = getChineseBoneName(selectedBone);
        selectedBoneSpan.textContent = `已选中: ${chineseName}`;
        selectedBoneSpan.style.color = '#2196f3';
        addButton.disabled = false;
    } else {
        selectedBoneSpan.textContent = '未选中骨骼';
        selectedBoneSpan.style.color = '#999';
        addButton.disabled = true;
    }
}

// 添加当前选中的骨骼和角度到序列
function addCurrentSelectionToSequence() {
    if (!selectedBone) {
        showWarning('请先选中一个骨骼', '动作编排');
        return;
    }
    
    const rotX = parseFloat(document.getElementById('rotate-x').value) || 0;
    const rotY = parseFloat(document.getElementById('rotate-y').value) || 0;
    const rotZ = parseFloat(document.getElementById('rotate-z').value) || 0;
    
    const chineseName = getChineseBoneName(selectedBone);
    
    actionSequence.push({
        id: Date.now(),
        boneName: selectedBone,
        chineseName: chineseName,
        rotationX: rotX,
        rotationY: rotY,
        rotationZ: rotZ
    });
    
    updateSequenceDisplay();
    showInfo(`已添加: ${chineseName} (X:${rotX}°, Y:${rotY}°, Z:${rotZ}°)`, '动作编排');
}

// 更新序列显示
function updateSequenceDisplay() {
    const sequenceList = document.getElementById('sequence-list');
    if (!sequenceList) return;
    
    if (actionSequence.length === 0) {
        sequenceList.innerHTML = '<div class="sequence-placeholder">选中骨骼并设置角度，然后点击"添加到序列"</div>';
        return;
    }
    
    sequenceList.innerHTML = '';
    actionSequence.forEach((item, index) => {
        const sequenceItem = document.createElement('div');
        sequenceItem.className = 'sequence-item';
        sequenceItem.innerHTML = `
            <span class="sequence-item-name">${index + 1}. ${item.chineseName} (X:${item.rotationX}°, Y:${item.rotationY}°, Z:${item.rotationZ}°)</span>
            <button class="sequence-item-remove" onclick="removeActionFromSequence(${item.id})">×</button>
        `;
        sequenceList.appendChild(sequenceItem);
    });
}

// 从序列中移除动作
function removeActionFromSequence(actionId) {
    actionSequence = actionSequence.filter(item => item.id !== actionId);
    updateSequenceDisplay();
}

// 清空动作序列
function clearActionSequence() {
    actionSequence = [];
    updateSequenceDisplay();
    showInfo('动作序列已清空', '动作编排');
}

// 生成随机动作
function generateRandomActions() {
    const countInput = document.getElementById('random-count');
    const count = parseInt(countInput.value) || 3;
    
    if (count < 1 || count > 20) {
        showWarning('随机动作数量应在1-20之间', '随机动作');
        return;
    }
    
    // 检查VRM模型是否已加载
    if (!window.currentVRM) {
        showWarning('VRM模型还在加载中，请稍等片刻后再试', '随机动作');
        console.log('尝试获取随机动作时VRM模型尚未加载完成');
        return;
    }
    
    if (!window.currentVRM.humanoid) {
        showWarning('VRM模型的humanoid数据未找到', '随机动作');
        return;
    }
    
    // 获取所有可用的骨骼名称
    const allBones = getAllAvailableBones();
    
    console.log('可用骨骼数量:', allBones.length);
    console.log('可用骨骼列表:', allBones);
    
    if (allBones.length === 0) {
        showWarning(`没有可用的骨骼。VRM模型状态: ${window.currentVRM ? '已加载' : '未加载'}`, '随机动作');
        return;
    }
    
    // 随机选择指定数量的骨骼
    const selectedBones = getRandomBones(allBones, count);
    
    // 为每个选中的骨骼生成随机角度并添加到序列
    selectedBones.forEach(boneName => {
        const randomAngles = generateRandomAngles();
        const chineseName = getChineseBoneName(boneName);
        
        actionSequence.push({
            id: Date.now() + Math.random(), // 确保唯一ID
            boneName: boneName,
            chineseName: chineseName,
            rotationX: randomAngles.x,
            rotationY: randomAngles.y,
            rotationZ: randomAngles.z
        });
    });
    
    updateSequenceDisplay();
    showSuccess(`已生成${selectedBones.length}个随机动作`, '随机动作');
}

// 检查VRM模型加载状态
function checkVRMStatus() {
    console.log('=== VRM模型状态检查 ===');
    console.log('window.currentVRM:', window.currentVRM);
    
    if (window.currentVRM) {
        console.log('VRM模型已加载');
        console.log('humanoid对象:', window.currentVRM.humanoid);
        
        if (window.currentVRM.humanoid) {
            console.log('humanBones对象:', window.currentVRM.humanoid.humanBones);
            const boneCount = Object.keys(window.currentVRM.humanoid.humanBones || {}).length;
            console.log('骨骼数量:', boneCount);
        } else {
            console.log('humanoid对象未找到');
        }
    } else {
        console.log('VRM模型未加载');
    }
    console.log('======================');
}

// 获取所有可用的骨骼名称
function getAllAvailableBones() {
    if (!window.currentVRM || !window.currentVRM.humanoid) {
        console.log('VRM模型或humanoid未加载');
        checkVRMStatus(); // 调用状态检查
        return [];
    }
    
    const bones = [];
    const humanBones = window.currentVRM.humanoid.humanBones;
    
    console.log('VRM humanBones对象:', humanBones);
    
    for (const name in humanBones) {
        if (humanBones[name]) {
            bones.push(name);
            console.log(`找到骨骼: ${name}`, humanBones[name]);
        }
    }
    
    console.log(`总共找到 ${bones.length} 个可用骨骼`);
    return bones;
}

// 随机选择指定数量的骨骼
function getRandomBones(allBones, count) {
    const shuffled = [...allBones].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, Math.min(count, allBones.length));
}

// 生成随机角度（合理范围内）
function generateRandomAngles() {
    // 为不同类型的动作生成合理的角度范围
    const angleRanges = {
        small: { min: -30, max: 30 },    // 小幅度动作
        medium: { min: -60, max: 60 },   // 中等幅度动作
        large: { min: -90, max: 90 }     // 大幅度动作
    };
    
    // 随机选择动作幅度
    const rangeTypes = ['small', 'medium', 'large'];
    const randomRange = rangeTypes[Math.floor(Math.random() * rangeTypes.length)];
    const range = angleRanges[randomRange];
    
    return {
        x: Math.round(Math.random() * (range.max - range.min) + range.min),
        y: Math.round(Math.random() * (range.max - range.min) + range.min),
        z: Math.round(Math.random() * (range.max - range.min) + range.min)
    };
}

// 执行动作序列
async function executeActionSequence() {
    if (actionSequence.length === 0) {
        showWarning('请先添加动作到序列中', '动作编排');
        return;
    }
    
    showInfo(`开始执行 ${actionSequence.length} 个骨骼动作`, '动作编排');
    
    for (let i = 0; i < actionSequence.length; i++) {
        const sequenceItem = actionSequence[i];
        
        // 高亮当前执行的动作
        highlightCurrentAction(i);
        
        // 转换角度为弧度
        const radX = (sequenceItem.rotationX * Math.PI) / 180;
        const radY = (sequenceItem.rotationY * Math.PI) / 180;
        const radZ = (sequenceItem.rotationZ * Math.PI) / 180;
        
        // 执行骨骼旋转
        if (rotateBone(sequenceItem.boneName, radX, radY, radZ)) {
            showInfo(`执行: ${sequenceItem.chineseName} 旋转`, '动作执行');
        }
        
        // 动作间的间隔
        if (i < actionSequence.length - 1) {
            await sleep(800);
        }
    }
    
    // 清除高亮
    clearActionHighlight();
    showInfo('🎉 动作序列执行完成', '动作编排');
}

// 高亮当前执行的动作
function highlightCurrentAction(index) {
    const sequenceItems = document.querySelectorAll('.sequence-item');
    sequenceItems.forEach((item, i) => {
        if (i === index) {
            item.style.background = '#e3f2fd';
            item.style.borderColor = '#2196f3';
        } else {
            item.style.background = 'white';
            item.style.borderColor = '#e1e3e4';
        }
    });
}

// 清除动作高亮
function clearActionHighlight() {
    const sequenceItems = document.querySelectorAll('.sequence-item');
    sequenceItems.forEach(item => {
        item.style.background = 'white';
        item.style.borderColor = '#e1e3e4';
    });
}

// 延时函数
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 更新VRM状态指示器
function updateVRMStatus(status, icon, text) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (indicator && statusText) {
        // 移除所有状态类
        indicator.className = 'status-indicator';
        // 添加新状态类
        indicator.classList.add(status);
        indicator.textContent = icon;
        statusText.textContent = text;
    }
}

// 切换人物朝向
function flipModelDirection() {
    if (!vrmModel) {
        showWarning('VRM模型尚未加载', '朝向调整');
        return;
    }
    
    // 当前Y轴旋转值
    const currentY = vrmModel.scene.rotation.y;
    
    // 切换朝向：如果接近0度，则转为180度；如果接近180度，则转为0度
    let newY;
    if (Math.abs(currentY) < Math.PI / 2) {
        // 当前朝向接近0度，转为180度
        newY = Math.PI;
        showInfo('人物已转为正面朝向', '朝向调整');
    } else {
        // 当前朝向接近180度，转为0度
        newY = 0;
        showInfo('人物已转为背面朝向', '朝向调整');
    }
    
    // 应用新的旋转
    vrmModel.scene.rotation.y = newY;
    
    // 更新配置以记住用户的选择
    VRM_CONFIG.initialRotation.y = newY;
    
    console.log(`人物朝向已调整为: ${(newY * 180 / Math.PI).toFixed(0)}度`);
}

console.log('骨骼控制系统已加载完成'); 