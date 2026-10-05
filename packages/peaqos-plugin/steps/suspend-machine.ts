import "server-only";

import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import { peaqWriteResult, subscriptionWrite } from "../lib/peaq-write";

type Result =
  | { success: true; transactionHash: string; chainId: number }
  | { success: false; error: string };

export type SuspendMachineCoreInput = { machineId: string };
export type SuspendMachineInput = StepInput & SuspendMachineCoreInput;

async function stepHandler(input: SuspendMachineCoreInput & StepInput): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const written = await subscriptionWrite(input, "suspend");
  if (!written.success) {
    return { success: false, error: written.error || "suspend failed" };
  }
  return peaqWriteResult(written);
}

export async function suspendMachineStep(input: SuspendMachineInput): Promise<Result> {
  "use step";
  return withStepLogging(input, () => stepHandler(input));
}

export const _integrationType = "peaqos";
