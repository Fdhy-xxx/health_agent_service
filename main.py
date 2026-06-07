import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

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


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/api/health-plan", summary="生成专属运动健康计划")
async def generate_health_plan(request_data: HealthPlanRequest):
    """
    接收 Java 服务端发来的用户身体数据，触发 LangGraph 状态机生成计划。
    """
    # 打印测试：看看 Pydantic 的大门保安是否正常工作
    print("====== 成功接收并校验来自 Java 端的数据 ======")
    print(f"身高: {request_data.height} cm")
    print(f"体重: {request_data.weight} kg")
    print(f"极限深蹲: {request_data.current_squat_1rm} kg")
    print(f"核心目标: {request_data.primary_goal}")
    if request_data.dormitory_rules:
        print(f"特殊限制: {request_data.dormitory_rules}")
    print("==============================================")

    # TODO: 这里即将接入 LangGraph 的入口代码
    # result = await run_health_agent(request_data)

    # 目前先返回一个测试用的 Mock 数据，证明接口通了
    return {
        "code": 200,
        "message": "AI 大脑已接收数据，LangGraph 节点暂未实装，敬请期待！",
        "data": {
            "received_status": "success",
            "next_step": "即将进入 Node 1 (Analyzer)"
        }
    }


if __name__ == "__main__":
    # 使用 uv 启动时，通常可以直接用命令行 `uvicorn main:app --reload`
    # 这里为了开发方便，也保留代码启动方式
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



