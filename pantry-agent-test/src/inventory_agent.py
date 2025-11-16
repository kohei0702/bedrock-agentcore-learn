import asyncio
from strands import Agent, tool
from strands_tools import use_aws
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from agent_executor import invoke


# エージェントの状態を管理
class InventoryAgentState:
    def __init__(self):
        self.queue = None

_state = InventoryAgentState()

def setup_inventory_agent(queue):
    """新規キューを受け取る"""
    _state.queue = queue
    return

def _create_agent():
    """サブエージェントを作成"""
    agent = Agent(
        model="apac.anthropic.claude-sonnet-4-20250514-v1:0",
        tools=[use_aws],
        system_prompt="""あなたは食材管理エージェントです。
「pantry-planner-ingredients」テーブルから在庫情報を取得します。
""",
    )
    return agent

@tool
async def inventory_agent(query):
    """食材管理エージェント"""
    result = await invoke(
        "食材管理エージェント",query,
        _create_agent, _state.queue
    )
    return result