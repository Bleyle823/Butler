import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import {
  ARC_TESTNET,
  USDC_ARC,
  asData,
  circleFetch,
  deriveIdempotencyKey,
} from "../lib/circle-api";

type TransferUsdcResult =
  | { success: true; transactionId: string }
  | { success: false; error: string };

export type TransferUsdcCoreInput = {
  walletId: string;
  destinationAddress: string;
  amount: string;
  jobId?: string;
};

export type TransferUsdcInput = StepInput &
  TransferUsdcCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: TransferUsdcCoreInput,
  credentials: CircleWalletsCredentials
): Promise<TransferUsdcResult> {
  if (!input.walletId || !input.destinationAddress || !input.amount) {
    return {
      success: false,
      error: "walletId, destinationAddress, and amount are required",
    };
  }

  const result = await circleFetch(
    credentials,
    "/v1/w3s/developer/transactions/transfer",
    {
      method: "POST",
      mutating: true,
      idempotencyKey: deriveIdempotencyKey(
        input.jobId || input.walletId,
        "transfer-usdc"
      ),
      body: {
        walletId: input.walletId,
        destinationAddress: input.destinationAddress,
        amounts: [input.amount],
        tokenId: undefined,
        tokenAddress: USDC_ARC,
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
    return { success: false, error: "Circle transfer returned no id" };
  }
  return { success: true, transactionId: id };
}

export async function transferUsdcStep(
  input: TransferUsdcInput
): Promise<TransferUsdcResult> {
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
