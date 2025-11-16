import * as cdk from "aws-cdk-lib/core";
import * as path from "path";
import { Construct } from "constructs";
import * as agentcore from "@aws-cdk/aws-bedrock-agentcore-alpha";
import * as iam from "aws-cdk-lib/aws-iam";

export class CdkAgentcoreStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const agentRuntimeArtifact = agentcore.AgentRuntimeArtifact.fromAsset(
      path.join(__dirname, "../agent")
    );

    const memory = new agentcore.Memory(this, "StrandsAgentsMemory", {
      memoryName: "cdk_agentcore_test_memory",
      memoryStrategies: [
        agentcore.MemoryStrategy.usingBuiltInSummarization(),
        agentcore.MemoryStrategy.usingBuiltInSemantic(),
        agentcore.MemoryStrategy.usingBuiltInUserPreference(),
      ],
    });

    const runtime = new agentcore.Runtime(this, "StrandsAgentsRuntime", {
      runtimeName: "cdk_agentcore_test",
      agentRuntimeArtifact: agentRuntimeArtifact,
      environmentVariables: {
        BEDROCK_AGENTCORE_MEMORY_ID: memory.memoryId,
      },
    });

    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ],
        resources: [
          `arn:aws:bedrock:*::foundation-model/*`,
          `arn:aws:bedrock:*:${this.account}:inference-profile/*`,
        ],
      })
    );

    // Bedrock AgentCore Memoryへのアクセス権限
    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "bedrock-agentcore:ListEvents",
          "bedrock-agentcore:GetEvent",
          "bedrock-agentcore:CreateEvent",
          "bedrock-agentcore:UpdateEvent",
          "bedrock-agentcore:DeleteEvent",
          "bedrock-agentcore:RetrieveEvents",
        ],
        resources: [memory.memoryArn],
      })
    );

    new cdk.CfnOutput(this, "RuntimeArn", {
      value: runtime.agentRuntimeArn,
    });
  }
}
