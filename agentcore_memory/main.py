import os
import time
from strands import Agent
from strands.models import BedrockModel
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager


REGION = os.getenv("AWS_REGION", "ap-northeast-1")
MODEL_ID = "apac.anthropic.claude-sonnet-4-20250514-v1:0"

memory_client = MemoryClient(region_name=REGION)

# メモリの作成
memory = memory_client.create_memory_and_wait(
    name="TestMemory",
    strategies=[
        {
            "summaryMemoryStrategy": {
                "name": "SessionSummarizer",
                "namespaces": ["/summaries/{actorId}/{sessionId}"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name": "PreferenceLearner",
                "namespaces": ["/preferences/{actorId}"]
            }
        },
        {
            "semanticMemoryStrategy": {
                "name": "FactExtractor",
                "namespaces": ["/facts/{actorId}"]
            }
        }
    ]
)

memory_id = memory.get('id')  # 事前に作成したメモリIDを指定
print(f"メモリID: {memory_id}")

actor_id = "actor-1234"
session_id = "session-A"

memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    session_id=session_id,
    actor_id=actor_id,

)

session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
    region_name=REGION
)

agent = Agent(
    model=MODEL_ID,
    session_manager=session_manager,
    system_prompt="""質問に対して丁寧に答えてください。""",
)

# エージェントの実行
agent("私は寿司が好きです。好きなネタはサーモンです。")

agent("私の趣味は海外旅行です。")

time.sleep(120)

# エージェントが持っている会話履歴
print("-" * 20)
print("エージェントが持っている会話履歴:")
print(agent.messages)

# 長期メモリ（ユーザプリファレンス）
print("-" * 20)
print("長期メモリ（ユーザプリファレンス）:")
memories = memory_client.retrieve_memories(
    memory_id=memory_id,
    namespace=f"/preferences/{actor_id}",
    query="ユーザの好みは？"
)
print(memories)

#---------------------- 別セッションでの確認------------------------
session_id = "session-B"

memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    session_id=session_id,
    actor_id=actor_id,
    retrieval_config={
        # ユーザーの好みや設定（actor全体）
        f"/preferences/{actor_id}": RetrievalConfig(
            top_k=5,
            relevance_score=0.1
        ),
    }
)

session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
    region_name=REGION
)

agent = Agent(
    model=MODEL_ID,
    session_manager=session_manager,
    system_prompt="""質問に対して丁寧に答えてください。""",
)

agent("私の好きなものは？")

print(agent.messages)