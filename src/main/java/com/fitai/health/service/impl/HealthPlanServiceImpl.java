package com.fitai.health.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.fitai.health.client.PythonAiClient;
import com.fitai.health.client.dto.AiHealthPlanResponse;
import com.fitai.health.mapper.UserHealthMapper;
import com.fitai.health.model.dto.HealthPlanRequestDTO;
import com.fitai.health.model.entity.UserHealthDO;
import com.fitai.health.service.HealthPlanService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;


@Slf4j
@Service
@RequiredArgsConstructor
public class HealthPlanServiceImpl implements HealthPlanService {

    private final UserHealthMapper userHealthMapper;
    // TODO: 待后续打通 client 包后注入 PythonAiClient
    private final PythonAiClient pythonAiClient; // 🌟 1. 注入你的新 Client

    @Override
    @Transactional(rollbackFor = Exception.class)
    public UserHealthDO createUserHealthPlan(HealthPlanRequestDTO requestDTO) {
        UserHealthDO userHealthDO = new UserHealthDO();
        BeanUtil.copyProperties(requestDTO, userHealthDO);

        // 🌟 2. 真正发起跨语言微服务调用！
        AiHealthPlanResponse aiResponse = pythonAiClient.requestHealthPlan(requestDTO);

        if (aiResponse != null && aiResponse.getData() != null) {
            // 🌟 3. 把大模型生成的专业文本精准提取并塞给 Entity
            userHealthDO.setAssessment(aiResponse.getData().getAssessment());
            userHealthDO.setTrainingPlan(aiResponse.getData().getTrainingPlan());
        }

        // 4. 持久化到 MySQL
        userHealthMapper.insert(userHealthDO);
        return userHealthDO;
    }
}