from pydantic import BaseModel, Field
from typing import Optional


class HealthPlanRequest(BaseModel):
    """
    接收 Java 业务侧发来的用户健康与目标数据
    """
    # 基础身体数据
    height: float = Field(
        ...,
        gt=50.0, lt=250.0,
        description="身高 (cm)，必须介于 50 到 250 之间",
        json_schema_extra={"example": 180.0}
    )
    weight: float = Field(
        ...,
        gt=20.0, lt=200.0,
        description="体重 (kg)，必须介于 20 到 200 之间",
        json_schema_extra={"example": 75.0}
    )

    # 运动能力指标
    current_squat_1rm: float = Field(
        ...,
        ge=0.0, lt=500.0,
        description="极限深蹲重量 1RM (kg)，没有训练经验可传 0",
        json_schema_extra={"example": 107.5}
    )

    # 主观诉求
    primary_goal: str = Field(
        ...,
        min_length=2, max_length=500,
        description="核心目标，如：实战扣篮、康复减脂等",
        json_schema_extra={"example": "提升垂直弹跳能力，目标完成实战扣篮"}
    )

    # 客观限制条件（可选）
    dormitory_rules: Optional[str] = Field(
        None,
        max_length=500,
        description="外部作息或场地限制条件",
        json_schema_extra={"example": "宿舍凌晨 1:00 准时断电熄灯"}
    )

    model_config = {
        "json_schema_extra": {
            "description": "健康管理系统核心分析接口请求体"
        }
    }