import asyncio
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from inventory_agent import inventory_agent, setup_inventory_agent
from recipe_agent import recipe_agent, setup_recipe_agent
from shopping_list_agent import shopping_list_agent, setup_shopping_list_agent
from stream_handler import merge_streams

def _create_orchestrator():
    """監督者エージェントを作成"""
    return Agent(
        model="apac.anthropic.claude-sonnet-4-20250514-v1:0",
        tools=[inventory_agent, recipe_agent, shopping_list_agent],
        system_prompt="""あなたは献立提案オーケストレーターです。
ユーザーの好みを考慮して、在庫情報を取得し、最適なレシピを提案するために、以下のエージェントを適切に呼び出してください。
- inventory_agent: 在庫情報を取得するエージェント
- recipe_agent: レシピを提案するエージェント
- shopping_list_agent: 買い物リストを作成するエージェント
最終的にユーザーの質問に答える形で、提案されたレシピを返してください。

ユーザーにレシピを確定していいかどうかを確認し、確定した場合には
recipe_agentとshopping_list_agentに確定するよう指示してください。
""",
    )

# アプリケーションを初期化
app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload):
    """呼び出し処理の開始地点"""
    prompt = payload.get("input", {}).get("prompt", "")

    # サブエージェント用のキューを初期化
    queue = asyncio.Queue()
    setup_inventory_agent(queue)
    setup_recipe_agent(queue)
    setup_shopping_list_agent(queue)

    try:
        orchestrator = _create_orchestrator()
        
        stream = orchestrator.stream_async(prompt)
        
        async for event in merge_streams(stream, queue):
            yield event
    finally:
        setup_inventory_agent(None)
        setup_recipe_agent(None)
        setup_shopping_list_agent(None)
# APIサーバーを起動
if __name__ == "__main__":
    app.run()

