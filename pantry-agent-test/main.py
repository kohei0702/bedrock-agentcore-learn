import os
from strands import Agent, tool
from strands_tools import use_aws
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = "ap-northeast-1"
MODEL_ID = "apac.anthropic.claude-sonnet-4-20250514-v1:0"

@tool
def inventory_agent(query: str):
    agent = Agent(
        model=MODEL_ID,
        tools=[use_aws],
        system_prompt="""あなたは食材管理エージェントです。
「pantry-planner-ingredients」テーブルから在庫情報を取得します。
""",
    )
    return str(agent(query))

@tool
def recipe_agent(query: str):
    agent = Agent(
        model=MODEL_ID,
        system_prompt="""あなたはレシピ提案エージェントです。
ユーザーの在庫情報をもとに、最適なレシピを提案します。
ユーザーがレシピを確定させた場合には「pantry-planner-meal-plans」テーブルに保存します。
""",
    )
    return str(agent(query))

@tool
def shopping_list_agent(query: str):
    agent = Agent(
        model=MODEL_ID,
        system_prompt="""あなたは買い物リスト作成エージェントです。
ユーザーの在庫情報とレシピ情報をもとに、必要な食材の買い物リストを作成します。
ユーザーがレシピを確定させた場合には「pantry-planner-shopping-lists」テーブルに保存します。
""",
    )
    return str(agent(query))

@app.entrypoint
async def invoke(payload, context):
    # actor_id = "quickstart-user"

    # Get runtime session ID for isolation
    # session_id = getattr(context, 'session_id', None)

    # Configure memory if available
    # session_manager = None
    # if MEMORY_ID:
    #     memory_config = AgentCoreMemoryConfig(
    #         memory_id=MEMORY_ID,
    #         session_id=session_id or 'default',
    #         actor_id=actor_id,
    #         retrieval_config={
    #             f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
    #             f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5)
    #         }
    #     )
    #     session_manager = AgentCoreMemorySessionManager(memory_config, REGION)

    # agent = Agent(
    #     model=MODEL_ID,
    #     # session_manager=session_manager,
    #     system_prompt="""あなたは献立提案アシスタントです。ユーザーの好みや過去の会話履歴を考慮して、毎日の食事の献立を提案します。栄養バランスや季節の食材も考慮してください。""",
    #     )

    orchestrator = Agent(
        model=MODEL_ID,
        system_prompt="""あなたは献立提案オーケストレーターです。
ユーザーの好みを考慮して、在庫情報を取得し、最適なレシピを提案するために、以下のエージェントを適切に呼び出してください。
- inventory_agent: 在庫情報を取得するエージェント
- recipe_agent: レシピを提案するエージェント
- shopping_list_agent: 買い物リストを作成するエージェント
最終的にユーザーの質問に答える形で、提案されたレシピを返してください。

ユーザーにレシピを確定していいかどうかを確認し、確定した場合には
recipe_agentとshopping_list_agentに確定するよう指示してください。
""",
        tools=[inventory_agent, recipe_agent, shopping_list_agent],
    )

    # 以下で呼び出す。
    # agentcore invoke '{"input": {"prompt": "献立を提案してください"}}'
    prompt = payload.get("input", {}).get("prompt", "")
    # result = orchestrator(prompt)

    # return {"response": result.message.get('content', [{}])[0].get('text', str(result))}

    print("prompt:", prompt)

    stream = orchestrator.stream_async(prompt)
    async for event in stream:
        print("event:", event)
        yield event
    yield {"type": "done"}
    
if __name__ == "__main__":
    app.run()