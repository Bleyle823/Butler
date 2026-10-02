import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import {
  ARC_TESTNET,
  asData,
  circleFetch,
  deriveIdempotencyKey,
} from "../lib/circle-api";

type ExecuteContractResult =
  | { success: true; transactionId: string }
  | { success: false; error: string };

export type ExecuteContractCoreInput = {
  walletId: string;
  contractAddress: string;
  abiFunctionSignature: string;
  abiParameters: string;
  jobId?: string;
};

export type ExecuteContractInput = StepInput &
  ExecuteContractCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: ExecuteContractCoreInput,
  credentials: CircleWalletsCredentials
): Promise<ExecuteContractResult> {
  if (
    !input.walletId ||
    !input.contractAddress ||
    !input.abiFunctionSignature
  ) {
    return {
      success: false,
      error: "walletId, contractAddress, and abiFunctionSignature are required",
    };
  }

  let params: unknown[] = [];
  try {
    params = input.abiParameters ? JSON.parse(input.abiParameters) : [];
    if (!Array.isArray(params)) {
      return { success: false, error: "abiParameters must be a JSON array" };
    }
  } catch {
    return { success: false, error: "abiParameters must be valid JSON" };
  }

  const result = await circleFetch(
    credentials,
    "/v1/w3s/developer/transactions/contractExecution",
    {
      method: "POST",
      mutating: true,
      idempotencyKey: deriveIdempotencyKey(
        input.jobId || input.walletId,
        `execute:${input.abiFunctionSignature}`
      ),
      body: {
        walletId: input.walletId,
        contractAddress: input.contractAddress,
        abiFunctionSignature: input.abiFunctionSignature,
        abiParameters: params,
        blockchain: ARC_TESTNET,
        feeLevel: "MEDIUM",
      },
    }
  );

  if (!result.ok) {
    return { success: false, error: result.error };
  }
  const data = asData(result.data);
  const id = String(data.id ?? data.transactionId ?? "");
  if (!id) {
    return { success: false, error: "Circle contractExecution returned no id" };
  }
  return { success: true, transactionId: id };
}

export async function executeContractStep(
  input: ExecuteContractInput
): Promise<ExecuteContractResult> {
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
