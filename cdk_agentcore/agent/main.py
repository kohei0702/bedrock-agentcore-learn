import os
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

REGION = os.getenv("AWS_REGION")
MODEL_ID = "apac.anthropic.claude-sonnet-4-20250514-v1:0"

@app.entrypoint
def invoke(payload, context):
    agent = Agent(
        model=MODEL_ID,
        system_prompt="""質問に対して丁寧に答えてください。""",
    )

    result = agent(payload.get("prompt", ""))
    return {"response": result.message.get('content', [{}])[0].get('text', str(result))}

if __name__ == "__main__":
    app.run()