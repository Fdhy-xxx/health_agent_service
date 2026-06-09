package com.fitai.health.controller;

import com.fitai.health.common.api.Result;
import com.fitai.health.model.dto.HealthPlanRequestDTO;
import com.fitai.health.model.entity.UserHealthDO;
import com.fitai.health.service.HealthPlanService;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class HealthPlanController {

    private final HealthPlanService healthPlanService;

    @PostMapping("/health-plan")
    public Result<UserHealthDO> generateHealthPlan(@Validated @RequestBody HealthPlanRequestDTO requestDTO) {
        // @Validated 触发 JSR-303 实体验证，自动拦截不合规参数（如年龄不合规）
        UserHealthDO resultData = healthPlanService.createUserHealthPlan(requestDTO);
        return Result.success("AI 大脑已完成分析并成功入库", resultData);
    }
}