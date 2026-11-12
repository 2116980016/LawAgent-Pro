import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from config import ALIYUN_API_KEY, LLM_MODEL
from tools import tools

# 配置日志（替代 print，显得更专业）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. 初始化 LLM (加入重试机制防 429)
logging.info("正在初始化大模型...")
llm = ChatOpenAI(
    model=LLM_MODEL,
    openai_api_key=ALIYUN_API_KEY,
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
    max_retries=3,        # 遇到限流自动重试3次
    request_timeout=30    # 30秒超时
)

# 2. 组装 Agent
logging.info("正在组装 Agent...")
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个专业的法律咨询助手。请严格依据检索到的法条和计算结果回答问题。如果检索不到相关法条，请如实告知用户，绝不要编造法律条文。遇到需要计算的金额，请务必调用 Calculator 工具。"
)

if __name__ == "__main__":
    # 测试一下 Agent 是否能被调用
    print("测试 Agent 启动...")
    res = agent.invoke({"messages": [{"role": "user", "content": "你好"}]})
    print(res["messages"][-1].content)