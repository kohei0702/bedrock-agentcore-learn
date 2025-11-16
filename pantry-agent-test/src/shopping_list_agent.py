import asyncio
from strands import Agent, tool
from strands_tools import use_aws
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from agent_executor import invoke


# エージェントの状態を管理
class ShoppingListAgentState:
    def __init__(self):
        self.queue = None

_state = ShoppingListAgentState()
def setup_shopping_list_agent(queue):
    """新規キューを受け取る"""
    _state.queue = queue
    return

def _create_agent():
    """サブエージェントを作成"""
    agent = Agent(
        model="apac.anthropic.claude-sonnet-4-20250514-v1:0",
        tools=[use_aws],
        system_prompt="""あなたは買い物リスト作成エージェントです。
ユーザーの在庫情報とレシピ情報をもとに、必要な食材の買い物リストを作成します。
ユーザーがレシピを確定させた場合には「pantry-planner-shopping-lists」テーブルに保存します。
""",
    )
    return agent

@tool
async def shopping_list_agent(query):
    """買い物リスト作成エージェント"""
    result = await invoke(
        "買い物リスト作成エージェント",query, 
        _create_agent, _state.queue
    )
    return result