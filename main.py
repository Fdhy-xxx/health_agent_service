import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from agent.graph import run_health_agent
# 导入拆分出去的路由组件
from routers.health_router import router as health_router
# 【关键】在导入任何自定义业务模块之前，先加载环境变量！
# 这样后续无论哪个文件需要用到 os.getenv("DEEPSEEK_API_KEY") 都能拿到
load_dotenv()

# 导入校验模型
from schemas.health_schema import HealthPlanRequest

# 初始化 FastAPI 实例
app = FastAPI(
    title="分布式智能运动健康管理系统",
    description="Python AI 中台 - 提供 LangGraph 状态机流转服务",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 注册路由组件
app.include_router(health_router)

@app.post("/api/health-plan", summary="生成专属运动健康计划")
async def generate_health_plan(request_data: HealthPlanRequest):
    """
    接收 Java 服务端发来的用户身体数据，触发 LangGraph 状态机生成计划。
    """
    # 打印测试：看看 Pydantic 的大门保安是否正常工作
    print("====== 成功接收并校验来自 Java 端的数据 ======")
    print(f"身高: {request_data.height} cm")
    print(f"体重: {request_data.weight} kg")
    print(f"动作类型: {request_data.movement_type}")
    print(f"极限重量: {request_data.current_1rm} kg")
    print(f"核心目标: {request_data.primary_goal}")
    if request_data.dormitory_rules:
        print(f"特殊限制: {request_data.dormitory_rules}")
    print("==============================================")

    # 将 Pydantic 模型转为 LangGraph State 所需的字典格式
    # 用一行代码直接搞定解包与字段初始化
    initial_state = {
        **request_data.model_dump(),  # 自动解包平铺前端传来的所有合法数据
        "assessment": None,
        "training_plan": None,
        "evaluation": None,
        "iteration_count": 0,
    }

    # 调用 LangGraph 状态机
    result = await run_health_agent.ainvoke(initial_state)
    return {
        "code": 200,
        "message": "AI 大脑已完成分析",
        "data": result
    }


if __name__ == "__main__":
    # 使用 uv 启动时，通常可以直接用命令行 `uvicorn main:app --reload`
    # 这里为了开发方便，也保留代码启动方式
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



