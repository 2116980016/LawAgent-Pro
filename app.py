import gradio as gr
from agent_core import agent

def chat_with_agent(message, history):
    if not message.strip():
        return "请输入有效问题。"
    
    # 构建包含历史记录的消息列表
    messages = []
    
    # 兼容新版和旧版 Gradio 的 history 格式
    if history:
        for item in history:
            if isinstance(item, dict):
                # 新版格式: {"role": "user", "content": "..."}
                messages.append({"role": item["role"], "content": item["content"]})
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                # 旧版格式: ("user_msg", "bot_msg")
                messages.append({"role": "user", "content": item[0]})
                messages.append({"role": "assistant", "content": item[1]})
                
    # 加上用户当前的新问题
    messages.append({"role": "user", "content": message})
    
    try:
        # 调用 Agent
        response = agent.invoke({"messages": messages})
        # 提取最后一条 AI 回复
        return response["messages"][-1].content
    except Exception as e:
        return f"系统报错：{str(e)}"

print("【步骤5】正在启动网页...")
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="⚖️ 智能法律咨询助手 (RAG + Agent 工程版)",
    description="具备双路混合检索、AST安全计算、多轮对话记忆。回答严格依据法律原文。",
    examples=[
        "男方多少岁可以结婚？",
        "如果违约金是 50000 元，按每天 0.05% 计算，逾期 30 天要赔多少钱？",
        "请问在中国，偷吃外星人判几年？"
    ]
)

if __name__ == "__main__":
    # inbrowser=True 会自动帮你打开浏览器
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)