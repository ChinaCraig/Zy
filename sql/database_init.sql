-- ===============================================
-- 虚拟人聊天系统数据库初始化脚本 - MySQL 8.0
-- Virtual Human Chat System Database Initialization
-- 包含所有表结构和更新内容
-- ===============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS virtual_human_chat 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE virtual_human_chat;

-- ===============================================
-- 聊天会话表 - Chat Sessions
-- ===============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '会话唯一标识',
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话ID（UUID）',
    user_identity VARCHAR(100) NOT NULL COMMENT '用户身份标识（姓名）',
    browser_info VARCHAR(500) NULL COMMENT '浏览器信息（User-Agent）',
    ip_address VARCHAR(45) NULL COMMENT '用户IP地址（支持IPv4和IPv6）',
    location_info VARCHAR(200) NULL COMMENT '地理位置信息（国家/城市）',
    session_start_time DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '会话开始时间',
    session_end_time DATETIME(3) NULL COMMENT '会话结束时间',
    total_messages INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '总消息数量',
    ai_provider VARCHAR(50) NOT NULL COMMENT 'AI提供商（openai/anthropic/deepseek等）',
    ai_model VARCHAR(100) NOT NULL COMMENT 'AI模型名称',
    session_status ENUM('active', 'ended', 'terminated') NOT NULL DEFAULT 'active' COMMENT '会话状态',
    end_reason ENUM('user_clear', 'browser_refresh', 'user_goodbye', 'limit_reached', 'manual') NULL COMMENT '结束原因',
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
    
    INDEX idx_user_identity (user_identity),
    INDEX idx_session_start (session_start_time),
    INDEX idx_session_status (session_status),
    INDEX idx_ip_address (ip_address),
    INDEX idx_session_time_ip (session_start_time, ip_address),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='聊天会话记录表';

-- ===============================================
-- 聊天消息表 - Chat Messages  
-- ===============================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息唯一标识',
    session_id VARCHAR(64) NOT NULL COMMENT '所属会话ID',
    message_order INT UNSIGNED NOT NULL COMMENT '消息在会话中的顺序号',
    sender_type ENUM('user', 'ai') NOT NULL COMMENT '发送方类型',
    sender_name VARCHAR(100) NULL COMMENT '发送方名称',
    message_content TEXT NOT NULL COMMENT '消息内容',
    message_tokens INT UNSIGNED NULL COMMENT '消息令牌数（如果可用）',
    message_time DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '消息发送时间',
    ai_provider VARCHAR(50) NULL COMMENT 'AI提供商（仅AI消息）',
    ai_model VARCHAR(100) NULL COMMENT 'AI模型（仅AI消息）',
    response_time_ms INT UNSIGNED NULL COMMENT 'AI响应时间（毫秒，仅AI消息）',
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    
    INDEX idx_session_id (session_id),
    INDEX idx_message_time (message_time),
    INDEX idx_sender_type (sender_type),
    INDEX idx_session_order (session_id, message_order),
    
    FOREIGN KEY fk_session (session_id) REFERENCES chat_sessions(session_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='聊天消息记录表';

-- ===============================================
-- 聊天统计视图 - Chat Statistics View
-- ===============================================
CREATE OR REPLACE VIEW chat_statistics AS
SELECT 
    DATE(cs.session_start_time) as chat_date,
    COUNT(DISTINCT cs.session_id) as total_sessions,
    COUNT(cm.id) as total_messages,
    AVG(cs.total_messages) as avg_messages_per_session,
    cs.ai_provider,
    cs.ai_model
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
GROUP BY DATE(cs.session_start_time), cs.ai_provider, cs.ai_model
ORDER BY chat_date DESC;

-- ===============================================
-- 用户聊天历史视图 - User Chat History View
-- ===============================================
CREATE OR REPLACE VIEW user_chat_history AS
SELECT 
    cs.user_identity,
    cs.session_id,
    cs.browser_info,
    cs.ip_address,
    cs.location_info,
    cs.session_start_time,
    cs.session_end_time,
    cs.total_messages,
    cs.session_status,
    cs.end_reason,
    cs.ai_provider,
    cs.ai_model,
    TIMESTAMPDIFF(MINUTE, cs.session_start_time, COALESCE(cs.session_end_time, NOW())) as session_duration_minutes
FROM chat_sessions cs
ORDER BY cs.user_identity, cs.session_start_time DESC;

-- ===============================================
-- 示例查询语句
-- ===============================================

-- 查询最近10个会话
-- SELECT * FROM chat_sessions ORDER BY session_start_time DESC LIMIT 10;

-- 查询特定用户的聊天历史  
-- SELECT * FROM user_chat_history WHERE user_identity = '小红' ORDER BY session_start_time DESC;

-- 查询特定会话的完整对话
-- SELECT 
--     cm.message_order,
--     cm.sender_type,
--     cm.sender_name,
--     cm.message_content,
--     cm.message_time
-- FROM chat_messages cm 
-- WHERE cm.session_id = 'your-session-id'
-- ORDER BY cm.message_order;

-- 查询每日聊天统计
-- SELECT * FROM chat_statistics ORDER BY chat_date DESC;

-- 查询用户IP地址统计
-- SELECT ip_address, COUNT(*) as session_count, 
--        MIN(session_start_time) as first_visit,
--        MAX(session_start_time) as last_visit
-- FROM chat_sessions 
-- WHERE ip_address IS NOT NULL
-- GROUP BY ip_address 
-- ORDER BY session_count DESC;

-- 查询浏览器使用统计
-- SELECT 
--     CASE 
--         WHEN browser_info LIKE '%Chrome%' THEN 'Chrome'
--         WHEN browser_info LIKE '%Firefox%' THEN 'Firefox'
--         WHEN browser_info LIKE '%Safari%' THEN 'Safari'
--         WHEN browser_info LIKE '%Edge%' THEN 'Edge'
--         ELSE 'Other'
--     END as browser_type,
--     COUNT(*) as usage_count
-- FROM chat_sessions 
-- WHERE browser_info IS NOT NULL
-- GROUP BY browser_type 
-- ORDER BY usage_count DESC; 