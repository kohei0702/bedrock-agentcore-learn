import asyncio
from strands import Agent, tool
from strands_tools import use_aws
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from agent_executor import invoke


# エージェントの状態を管理
class RecipeAgentState:
    def __init__(self):
        self.queue = None

_state = RecipeAgentState()

def setup_recipe_agent(queue):
    """新規キューを受け取る"""
    _state.queue = queue
    return

def _create_agent():
    """サブエージェントを作成"""
    agent = Agent(
        model="apac.anthropic.claude-sonnet-4-20250514-v1:0",
        tools=[use_aws],
        system_prompt="""あなたはレシピ提案エージェントです。
ユーザーの在庫情報をもとに、最適なレシピを提案します。
ユーザーがレシピを確定させた場合には「pantry-planner-meal-plans」テーブルに保存します。
""",
    )
    return agent

@tool
async def recipe_agent(query):
    """レシピ提案エージェント"""
    result = await invoke(
        "レシピ提案エージェント",query,
        _create_agent, _state.queue
    )
    return result