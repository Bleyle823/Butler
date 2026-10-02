import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { asData, circleFetch } from "../lib/circle-api";

type WaitResult =
  | { success: true; state: string; txHash: string }
  | { success: false; error: string; state?: string };

export type WaitForTransactionCoreInput = {
  transactionId: string;
};

export type WaitForTransactionInput = StepInput &
  WaitForTransactionCoreInput & {
    integrationId?: string;
  };

const TERMINAL_OK = new Set(["COMPLETE", "CONFIRMED", "COMPLETED"]);
const TERMINAL_FAIL = new Set(["FAILED", "CANCELLED", "DENIED", "EXPIRED"]);

async function stepHandler(
  input: WaitForTransactionCoreInput,
  credentials: CircleWalletsCredentials
): Promise<WaitResult> {
  if (!input.transactionId) {
    return { success: false, error: "transactionId is required" };
  }

  const maxAttempts = 40;
  const delayMs = 3000;

  for (let i = 0; i < maxAttempts; i += 1) {
    const result = await circleFetch(
      credentials,
      `/v1/w3s/transactions/${encodeURIComponent(input.transactionId)}`,
      { method: "GET" }
    );
    if (!result.ok) {
      return { success: false, error: result.error };
    }
    const data = asData(result.data);
    const tx = (data.transaction as Record<string, unknown> | undefined) ?? data;
    const state = String(tx.state ?? tx.status ?? "");
    const txHash = String(tx.txHash ?? tx.transactionHash ?? "");
    if (TERMINAL_OK.has(state)) {
      return { success: true, state, txHash };
    }
    if (TERMINAL_FAIL.has(state)) {
      return {
        success: false,
        error: `Circle transaction ${state}`,
        state,
      };
    }
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }

  return { success: false, error: "Timed out waiting for Circle transaction" };
}

export async function waitForTransactionStep(
  input: WaitForTransactionInput
): Promise<WaitResult> {
  "use step";

  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};

  return withStepLogging(input, () =>
    stepHandler(input, credentials as CircleWalletsCredentials)
  );
}

export const _integrationType = "circle-wallets";
