import os
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION")
MODEL_ID = "apac.anthropic.claude-sonnet-4-20250514-v1:0"

@app.entrypoint
def invoke(payload, context):
    actor_id = "quickstart-user"


    session_id = getattr(context, 'session_id', None)


    # Set up memory session manager if MEMORY_ID is providmcped
    session_manager = None
    if MEMORY_ID:
        memory_config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id = session_id or "default",
            actor_id = actor_id,
            retrieval_config = {}
        )
        session_manager = AgentCoreMemorySessionManager(memory_config, REGION)




    agent = Agent(
        model=MODEL_ID,
        session_manager=session_manager,
        system_prompt="""質問に対して丁寧に答えてください。
ユーザーの過去の会話や好みを記憶し、それを活用してください。
特に、ユーザーが「好き」「嫌い」などの好みを述べた場合は、しっかり記憶してください。""",
    )

    result = agent(payload.get("prompt", ""))
    return {"response": result.message.get('content', [{}])[0].get('text', str(result))}

if __name__ == "__main__":
    app.run()