# Discord斜杠命令中文本地化补丁
# 版本: 5d3be898a-discord1
# 范围: 仅汉化斜杠命令名称、描述和触发后的固定回复文案

# 本文件定义了需要汉化的Discord斜杠命令内容
# 实际补丁通过patch文件应用

COMMANDS_ZH = {
    # 斜杠命令名称汉化
    "slash_command_names": {
        "new": "新会话",
        "reset": "重置",
        "model": "模型",
        "reasoning": "推理",
        "personality": "人格",
        "retry": "重试",
        "undo": "撤销",
        "status": "状态",
        "sethome": "设为主页",
        "stop": "停止",
        "steer": "注入",
        "compress": "压缩",
        "title": "标题",
        "resume": "恢复",
        "usage": "用量",
        "help": "帮助",
        "insights": "洞察",
        "reload-mcp": "重载MCP",
        "reload-skills": "重载技能",
        "voice": "语音",
        "update": "更新",
        "restart": "重启",
        "approve": "批准",
        "deny": "拒绝",
        "thread": "线程",
        "queue": "队列",
        "background": "后台",
    },
    
    # 斜杠命令描述汉化
    "slash_command_descriptions": {
        "new": "开始新会话",
        "reset": "重置当前会话",
        "model": "显示或切换模型",
        "reasoning": "显示或切换推理强度",
        "personality": "设置人格",
        "retry": "重试上一条消息",
        "undo": "删除上一轮对话",
        "status": "显示当前会话状态",
        "sethome": "将此频道设为主页",
        "stop": "停止正在运行的Hermes",
        "steer": "在下一轮工具调用后注入消息",
        "compress": "压缩对话上下文",
        "title": "设置或显示会话标题",
        "resume": "恢复之前的命名会话",
        "usage": "显示当前会话的token用量",
        "help": "显示可用命令",
        "insights": "显示用量洞察与分析",
        "reload-mcp": "从配置重载MCP服务器",
        "reload-skills": "重新扫描技能目录",
        "voice": "切换语音回复模式",
        "update": "更新Hermes到最新版本",
        "restart": "优雅重启网关",
        "approve": "批准待处理的危险命令",
        "deny": "拒绝待处理的危险命令",
        "thread": "创建新线程并在其中启动会话",
        "queue": "将提示词排入下一轮",
        "background": "在后台运行提示词",
    },
    
    # 参数描述汉化
    "parameter_descriptions": {
        "name": "名称",
        "effort": "推理强度: none, minimal, low, medium, high, xhigh",
        "prompt": "要注入的文本",
        "args": "参数",
        "days": "分析天数",
        "scope": "范围: 'all', 'session', 'always'",
        "message": "消息内容",
        "mode": "模式: on, off, tts, channel, leave, status",
    },
    
    # Choice选项汉化
    "choice_names": {
        "channel — join your voice channel": "加入语音频道",
        "leave — leave voice channel": "离开语音频道",
        "on — voice reply to voice messages": "语音回复语音消息",
        "tts — voice reply to all messages": "语音回复所有消息",
        "off — text only": "仅文本",
        "status — show current mode": "显示当前模式",
    },
    
    # 固定回复文案汉化
    "fixed_responses": {
        "New conversation started~": "新会话已开始~",
        "Session reset~": "会话已重置~",
        "Status sent~": "状态已发送~",
        "Stop requested~": "停止请求已发送~",
        "Retrying~": "正在重试~",
        "Update initiated~": "更新已启动~",
        "Restart requested~": "重启请求已发送~",
        "Queued for the next turn.": "已排入下一轮",
        "Background task started~": "后台任务已启动~",
    },
}
