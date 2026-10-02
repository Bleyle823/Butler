import "server-only";

import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import { subscriptionWrite } from "../lib/peaq-write";

type Result =
  | { success: true; transactionHash: string }
  | { success: false; error: string };

export type RenewSubscriptionCoreInput = { machineId: string };
export type RenewSubscriptionInput = StepInput & RenewSubscriptionCoreInput;

async function stepHandler(input: RenewSubscriptionCoreInput & StepInput): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const written = await subscriptionWrite(input, "renew");
  if (!written.success) {
    return { success: false, error: written.error || "renew failed" };
  }
  return {
    success: true,
    transactionHash: String(
      (written as { transactionHash?: string }).transactionHash || ""
    ),
  };
}

export async function renewSubscriptionStep(input: RenewSubscriptionInput): Promise<Result> {
  "use step";
  return withStepLogging(input, () => stepHandler(input));
}

export const _integrationType = "peaqos";
