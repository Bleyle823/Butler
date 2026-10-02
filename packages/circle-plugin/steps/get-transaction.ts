import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { asData, circleFetch } from "../lib/circle-api";

type GetTransactionResult =
  | { success: true; state: string; txHash: string }
  | { success: false; error: string };

export type GetTransactionCoreInput = {
  transactionId: string;
};

export type GetTransactionInput = StepInput &
  GetTransactionCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: GetTransactionCoreInput,
  credentials: CircleWalletsCredentials
): Promise<GetTransactionResult> {
  if (!input.transactionId) {
    return { success: false, error: "transactionId is required" };
  }
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
  return {
    success: true,
    state: String(tx.state ?? tx.status ?? ""),
    txHash: String(tx.txHash ?? tx.transactionHash ?? ""),
  };
}

export async function getTransactionStep(
  input: GetTransactionInput
): Promise<GetTransactionResult> {
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
