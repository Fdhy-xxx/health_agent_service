package com.fitai.health.client;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONUtil;
import com.fitai.health.client.dto.AiHealthPlanResponse;
import com.fitai.health.model.dto.HealthPlanRequestDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class PythonAiClient {

    // 🔑 动态读取 application.yml 中的 Python 接口路径
    @Value("${ai-service.url}")
    private String aiServiceUrl;

    /**
     * 调用 Python FastAPI 智能体中台
     * @param requestDTO Java 侧接收到的标准身体与目标数据
     * @return 解析完毕的 AI 分析与训练计划响应体
     */
    public AiHealthPlanResponse requestHealthPlan(HealthPlanRequestDTO requestDTO) {
        log.info("==== [防腐层] 开始组装数据并发起 AI 算力中台调用 ====");

        // 1. 利用 Hutool 将 Java DTO 极速转化为序列化 JSON 字符串
        // ==== [防腐层核心功能] 将 Java 的驼峰命名翻译为 Python 的下划线命名 ====
        cn.hutool.json.JSONObject pythonPayload = new cn.hutool.json.JSONObject();
        pythonPayload.set("age", requestDTO.getAge());
        pythonPayload.set("height", requestDTO.getHeight());
        pythonPayload.set("weight", requestDTO.getWeight());

        // 🌟 重点翻译以下四个字段
        pythonPayload.set("movement_type", requestDTO.getMovementType());
        pythonPayload.set("current_1rm", requestDTO.getCurrent1rm());
        pythonPayload.set("primary_goal", requestDTO.getPrimaryGoal());
        pythonPayload.set("dormitory_rules", requestDTO.getDormitoryRules());

        String jsonPayload = pythonPayload.toString();
        log.info("翻译后发送给 Python 端的 Payload: {}", jsonPayload);
        log.info("发送给 Python 端的 Payload: {}", jsonPayload);

        try {
            // 2. 发起同步 HTTP POST 请求，死等 Python 端大模型分析（大概 10~15 秒）
            // 💡 提示：后续引入 RocketMQ 后，这段“死等”逻辑会被移入 MQ 消费者中，彻底解耦主线程！
            log.info("正在向 AI 引擎发起网络请求，地址: {} ...", aiServiceUrl);
            // 设置 120 秒 (120000毫秒) 的超长等待时间
            String responseJson = HttpRequest.post(aiServiceUrl)
                    .body(jsonPayload)
                    .timeout(120000) // 🌟 核心：给大模型两分钟的思考时间
                    .execute()
                    .body();

            log.info("==== [防腐层] AI 中台响应成功 ====");

            // 3. 将返回的复杂大 JSON 反序列化映射为 Java 对象
            return JSONUtil.toBean(responseJson, AiHealthPlanResponse.class);

        } catch (Exception e) {
            log.error("❌ 调用 Python AI 服务发生致命网络异常或超时", e);
            throw new RuntimeException("AI中台算力引擎暂时不可用，请稍后再试");
        }
    }
}