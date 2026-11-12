import ast
import operator as op
from langchain_core.tools import Tool
from database import get_ensemble_retriever

# ==========================================
# 1. 安全计算器 (使用 AST 白名单防注入)
# ==========================================
# 允许的数学操作符
OPERATORS = {
    ast.Add: op.add,      # 加
    ast.Sub: op.sub,      # 减
    ast.Mult: op.mul,     # 乘
    ast.Div: op.truediv,  # 除
    ast.Pow: op.pow,      # 幂
    ast.USub: op.neg      # 负号
}

def safe_eval(node):
    """递归解析 AST 节点，只允许白名单内的操作"""
    if isinstance(node, ast.Num): # Python < 3.8
        return node.n
    elif isinstance(node, ast.Constant): # Python >= 3.8
        return node.value
    elif isinstance(node, ast.BinOp):
        return OPERATORS[type(node.op)](safe_eval(node.left), safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return OPERATORS[type(node.op)](safe_eval(node.operand))
    else:
        raise TypeError(f"不支持的表达式类型: {node}")

def calculate_math(expression: str) -> str:
    print(f"\n[🔧 触发工具] 正在计算金额：{expression}")
    try:
        # 把百分号转换掉
        expr = expression.replace("%", "/100").replace("×", "*").replace("÷", "/")
        
        # 使用 ast 解析成语法树
        node = ast.parse(expr, mode='eval').body
        result = safe_eval(node)
        
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算失败，请检查表达式是否合法。错误：{e}"

# ==========================================
# 2. 法律检索工具
# ==========================================
# 延迟初始化检索器
_retriever = None

def search_law(query: str) -> str:
    global _retriever
    if _retriever is None:
        _retriever = get_ensemble_retriever()
        
    print(f"\n[🔧 触发工具] 正在检索法条：{query}")
    docs = _retriever.invoke(query)
    
    if not docs:
        return "未检索到相关法条，请直接告诉用户你不知道。"
        
    # 拼接检索结果，带上编号方便溯源
    context = "\n\n".join([f"[片段{i+1}]: {doc.page_content}" for i, doc in enumerate(docs)])
    return context

# ==========================================
# 3. 封装为 Agent 可用的 Tool
# ==========================================
tools = [
    Tool(
        name="Law_Search",
        func=search_law,
        description="当用户询问法律条款、规定、赔偿标准、或者特定法律名词时使用。输入必须是一个完整的法律问题。如果查不到，不要编造。"
    ),
    Tool(
        name="Calculator",
        func=calculate_math,
        description="当用户需要计算违约金、赔偿金、利息、加减乘除时使用。输入必须是合法的数学表达式，如 '50000 * 0.0005 * 30'。注意把百分号转换为小数。"
    )
]

if __name__ == "__main__":
    # 测试安全计算
    print(calculate_math("50000 * 0.05 / 100 * 30"))
    # 测试注入攻击（会被拦截）
    print(calculate_math("__import__('os').system('dir')"))