import "server-only";

import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import { peaqWriteResult, submitEventWrite } from "../lib/peaq-write";

type Result =
  | { success: true; transactionHash: string; chainId: number }
  | { success: false; error: string };

export type RecordActivityCoreInput = {
  machineId: string;
  value?: string;
  rawData?: string;
};

export type RecordActivityInput = StepInput & RecordActivityCoreInput;

async function stepHandler(input: RecordActivityCoreInput & StepInput): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const written = await submitEventWrite({
    ...input,
    eventType: 1,
    value: input.value || "0",
    rawData: input.rawData || "activity",
    trustLevel: "0",
    sourceChainId: "0",
    sourceTxHash: "",
    currency: "",
  });
  if (!written.success) {
    return { success: false, error: written.error || "submitEvent failed" };
  }
  return peaqWriteResult(written);
}

export async function recordActivityStep(input: RecordActivityInput): Promise<Result> {
  "use step";
  return withStepLogging(input, () => stepHandler(input));
}

export const _integrationType = "peaqos";
