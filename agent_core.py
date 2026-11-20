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
    system_prompt="""你是一个专业的法律咨询助手。请严格依据检索到的法条回答问题。

判断流程（必须遵守）：
1. 拿到 Law_Search 的检索结果后，先判断：这些片段是否直接回答了用户的问题？
2. 如果片段与问题明显无关（例如问刑法问题却只检索到民法条文，或问的是知识库外的事物），必须如实告知：
   “我检索到的法条与您的问题无关，无法给出可靠回答。”
   绝不能拿不相关的法条硬套，更不能编造。
3. 如果工具返回“未检索到相关法条”，直接告知用户你不知道。
4. 遇到需要计算的金额，务必调用 Calculator 工具。"""
)

if __name__ == "__main__":
    # 测试一下 Agent 是否能被调用
    print("测试 Agent 启动...")
    res = agent.invoke({"messages": [{"role": "user", "content": "你好"}]})
    print(res["messages"][-1].content)