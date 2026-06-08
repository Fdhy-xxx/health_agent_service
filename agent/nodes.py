from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agent.state import HealthAgentState
from config.llm_config import llm

# 这里假设你把之前的专家提示词写在了 agent/prompts.py 里
# 如果没写，你可以直接把一大段提示词字符串赋给这个变量
from agent.prompts import ANALYZER_SYSTEM_PROMPT, GENERATOR_SYSTEM_PROMPT


def analyzer_node(state: HealthAgentState):
    # 1. 你的极佳亮点：提前算出 BMI
    bmi = state["weight"] / ((state["height"] / 100) ** 2)
    print(f">>> 后台计算得出 BMI: {bmi:.2f}")

    # 2. 把所有冷数据组装成“人话”，发给大模型
    user_context = f"""
    请评估以下用户：
    - 身高: {state['height']} cm
    - 体重: {state['weight']} kg
    - 实际计算 BMI: {bmi:.2f}
    - {state.get('movement_type', '深蹲')}极限重量(1RM): {state.get('current_1rm', 0)} kg
    - 核心目标: {state['primary_goal']}
    """

    # 3. 使用规范的消息列表：【系统人设】 + 【用户数据】
    messages = [
        SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=user_context)
    ]

    # 4. 触发大模型思考
    print(">>> 正在调用大模型生成体测评估...")
    response = llm.invoke(messages)

    # 5. 更新 State 中的 assessment 字段
    return {"assessment": response.content}


from langchain_core.messages import SystemMessage, HumanMessage  # 删除了没用的 AIMessage
from agent.state import HealthAgentState
from config.llm_config import llm
from agent.prompts import GENERATOR_SYSTEM_PROMPT


def generator_node(state: HealthAgentState):
    print(">>> 正在调用大模型定制化计划生成...")

    # 1. 防御性编程：拿到上游结果，如果没有直接报错拦截
    upstream_assessment = state.get("assessment")
    if not upstream_assessment:
        raise ValueError("Node 2 致命错误：未能获取上游身体评估报告！")

    # 2. 组装最强上下文：评估报告 + 核心目标 + 外部限制全覆盖！
    generation_context = f"""
    请根据以下上游提供的专业评估报告，定制专属训练与饮食方案：
    【身体评估报告】
    {upstream_assessment}
    【用户的核心目标】
    {state['primary_goal']}
    【用户的客观限制条件】
    {state.get('dormitory_rules', '无特殊限制')}
    """

    # 3. 严格使用 HumanMessage 传递上下文
    messages = [
        SystemMessage(content=GENERATOR_SYSTEM_PROMPT),
        HumanMessage(content=generation_context)
    ]

    # 4. 触发大模型思考
    response = llm.invoke(messages)

    # 5. 更新 State 中的 training_plan 字段
    return {"training_plan": response.content}