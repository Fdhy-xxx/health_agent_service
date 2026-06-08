from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.constants import END

from agent.state import HealthAgentState, EvaluationResult
from config.llm_config import llm

# 这里假设你把之前的专家提示词写在了 agent/prompts.py 里
# 如果没写，你可以直接把一大段提示词字符串赋给这个变量
from agent.prompts import ANALYZER_SYSTEM_PROMPT, GENERATOR_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT


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

    # 【新增核心逻辑】：读取上一轮的毒舌反馈
    eval_result = state.get("evaluation")
    feedback_context = ""
    # 如果有打分结果，并且是不合格，就把找茬意见提取出来
    if eval_result and eval_result.get("grade") == "fail":
        feedback_context = f"""
        【⚠️ 极高优先级修正指令】
        你上一版生成的计划已被审查专家打回！
        打回原因：{eval_result.get('feedback')}
        本次生成请务必解决上述致命问题，切勿重犯！
        """

    # 2. 组装最强上下文：评估报告 + 核心目标 + 外部限制全覆盖！
    # 将反馈拼接到大模型的上下文中
    generation_context = f"""
    请根据以下上游提供的专业评估报告，定制专属训练与饮食方案：
    【身体评估报告】
    {upstream_assessment}
    【用户的核心目标】
    {state['primary_goal']}
    【用户的客观限制条件】
    {state.get('dormitory_rules', '无特殊限制')}
    {feedback_context}  <-- 动态注入反馈
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


def evaluator_node(state: HealthAgentState):
    # 1. 绑定结构化输出（魔法就在这一行）
    evaluator_llm = llm.with_structured_output(EvaluationResult)
    # ... 组装上下文 messages 的代码 ...

    # 防御性编程：拿到上游结果，如果没有直接报错拦截
    upstream_training_plan = state.get("training_plan")
    if not upstream_training_plan:
        raise ValueError("Node 3 致命错误：未能获取上游训练与饮食方案！")

    # 组装上下文：评估报告 + 核心目标 + 外部限制全覆盖！
    evaluator_context = f"""
        请根据以下上游提供的训练与饮食方案，评估方案可行性：
        【训练与饮食方案】
        {upstream_training_plan}
        【用户的核心目标】
        {state['primary_goal']}
        【用户的客观限制条件】
        {state.get('dormitory_rules', '无特殊限制')}
        """

    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=evaluator_context)
    ]

    # 2. 调用约束版的大模型
    response = evaluator_llm.invoke(messages)

    # 此时的 response 已经不再是普通的字符串了！
    # 它是一个完美的 EvaluationResult 类的实例，你可以直接 . 点出属性
    print(f"打分结果: {response.grade}")
    print(f"毒舌反馈: {response.feedback}")

    # 【新增核心逻辑】：每次审查完，让迭代次数 + 1
    current_iteration = state.get("iteration_count", 0) + 1
    print(f">>> 当前优化迭代轮数: {current_iteration}")

    # 同时返回更新后的 evaluation 和 iteration_count
    return {
        "evaluation": response.model_dump(),
        "iteration_count": current_iteration
    }


def route_after_eval(state: HealthAgentState) -> Literal["generator", "__end__"]:
    """评估后路由：pass→结束，fail→重新生成，超过3轮强制终止"""

    eval_result = state.get("evaluation", {})
    iteration_count = state.get("iteration_count", 0)

    # 1. 正常通过
    if eval_result.get("grade") == "pass":
        print("  ✓ 评估通过！准备将完美计划返回给前端。")
        return END

    # 2. 触发熔断机制（到达最大次数，强行停止内耗）
    if iteration_count >= 3:
        print(f"  ⚠ 触发系统熔断！已达到最大重试次数 (3次)，强制终止死循环，按当前最终版本输出。")
        return END

    # 3. 正常打回重造
    print(f"  ⚠ 评估未通过，打回 Node 2 重写。原因：{eval_result.get('feedback')}")
    return "generator"
