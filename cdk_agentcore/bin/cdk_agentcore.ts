#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";
import { CdkAgentcoreStack } from "../lib/cdk_agentcore-stack";

const app = new cdk.App();
new CdkAgentcoreStack(app, "CdkAgentcoreStack", {});
