package com.fitai.health.model.dto;

import cn.hutool.core.annotation.Alias;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class AiHealthPlanResponse {
    private Integer code;
    private String message;
    private PythonData data;

    @Data
    public static class PythonData {
        private String assessment;

        // 告诉 Hutool，当看到 JSON 里的 training_plan 时，就塞到这个字段里
        @Alias("training_plan")
        private String trainingPlan;

        @Alias("plan_generated")
        private Boolean planGenerated;

        @Alias("is_ready")
        private Boolean isReady;

        @Alias("iteration_count")
        private Integer iterationCount;

        private Double height;
        private Double weight;
        private Integer age;

        @Alias("primary_goal")
        private String primaryGoal;
    }
}