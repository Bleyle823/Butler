import "server-only";

import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import { validateRevenue } from "../lib/peaq-api";
import { submitEventWrite } from "../lib/peaq-write";

type Result =
  | { success: true; transactionHash: string }
  | { success: false; error: string };

export type RecordRevenueCoreInput = {
  machineId: string;
  value: string;
  currency?: string;
  sourceChainId?: string;
  trustLevel?: string;
  sourceTxHash?: string;
  rawData?: string;
};

export type RecordRevenueInput = StepInput & RecordRevenueCoreInput;

async function stepHandler(input: RecordRevenueCoreInput & StepInput): Promise<Result> {
  if (!input.machineId || !input.value) {
    return { success: false, error: "machineId and value are required" };
  }
  const currency = (input.currency || "USD").toUpperCase();
  const sourceChainId = input.sourceChainId ?? "0";
  const trustLevel = input.trustLevel ?? "0";
  const check = validateRevenue({
    value: input.value,
    currency,
    sourceChainId,
    trustLevel,
  });
  if (!check.ok) {
    return check;
  }
  const rawData =
    input.rawData ||
    (input.sourceTxHash ? `arc:${input.sourceTxHash}` : "arc");
  const written = await submitEventWrite({
    ...input,
    eventType: 0,
    rawData,
    trustLevel,
    sourceChainId,
    sourceTxHash: input.sourceTxHash || "",
    currency,
  });
  if (!written.success) {
    return { success: false, error: written.error || "submitEvent failed" };
  }
  return {
    success: true,
    transactionHash: String(
      (written as { transactionHash?: string }).transactionHash || ""
    ),
  };
}

export async function recordRevenueStep(input: RecordRevenueInput): Promise<Result> {
  "use step";
  return withStepLogging(input, () => stepHandler(input));
}

export const _integrationType = "peaqos";
