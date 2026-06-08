from typing import TypedDict, Optional, List, Literal

from pydantic import BaseModel, Field



# class EvaluationResult(TypedDict):
#     grade: Literal["pass", "fail"]  # 状态机路由的唯一依据
#     feedback: str  # 找茬反馈意见，如果是不合格，需要写明原因

# 1. 定义专家审查结果的结构化输出（用于 Evaluator 节点）
class EvaluationResult(BaseModel):
    grade: Literal["pass", "fail"] = Field(
        description="最终打分，必须是 pass 或 fail"
    )
    feedback: str = Field(
        description="找茬反馈意见，如果是 fail，必须给出明确的修改方向"
    )

# 2. 核心：共享状态托盘（流转于各个 Node 之间）
class HealthAgentState(TypedDict):
    # --- 原始输入层（Java 侧传过来的冷数据，之后无法重建） ---
    height: float  # 身高 (cm)
    weight: float  # 体重 (kg)
    movement_type: str  # 运动能力指标(拆分为动作和重量)
    current_1rm: float  # 极限深蹲,卧推重量 (kg)
    primary_goal: str  # 核心目标（例如：实战扣篮、减脂）
    dormitory_rules: str  # 外部作息限制（例如：1:00 准时断电）

    # --- 流程演进层（被后续多个节点所需、重新获取成本高的数据） ---
    assessment: Optional[str]  # Analyzer 节点生成的身体代谢和力量评估报告
    training_plan: Optional[str]  # Generator 节点生成的初版/改版训练计划

    # --- 门控路由层（决策大脑） ---
    evaluation: Optional[EvaluationResult]  # Evaluator 节点写入的审查结果
    iteration_count: int  # 记录当前优化迭代了几轮，防止死循环