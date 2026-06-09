package com.fitai.health.service;

import com.fitai.health.model.dto.HealthPlanRequestDTO;
import com.fitai.health.model.entity.UserHealthDO;

public interface HealthPlanService {
    /**
     * 分析用户健康状态并生成训练计划
     * @param requestDTO 前端/Java业务侧传入的表单数据
     * @return 包含AI生成计划的完整领域对象
     */
    UserHealthDO createUserHealthPlan(HealthPlanRequestDTO requestDTO);
}