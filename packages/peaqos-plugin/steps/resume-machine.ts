import "server-only";

import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import { peaqWriteResult, subscriptionWrite } from "../lib/peaq-write";

type Result =
  | { success: true; transactionHash: string; chainId: number }
  | { success: false; error: string };

export type ResumeMachineCoreInput = { machineId: string };
export type ResumeMachineInput = StepInput & ResumeMachineCoreInput;

async function stepHandler(input: ResumeMachineCoreInput & StepInput): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const written = await subscriptionWrite(input, "resume");
  if (!written.success) {
    return { success: false, error: written.error || "resume failed" };
  }
  return peaqWriteResult(written);
}

export async function resumeMachineStep(input: ResumeMachineInput): Promise<Result> {
  "use step";
  return withStepLogging(input, () => stepHandler(input));
}

export const _integrationType = "peaqos";
