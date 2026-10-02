import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { ARC_TESTNET, asData, circleFetch, freshUuid } from "../lib/circle-api";

type CreateWalletResult =
  | { success: true; walletId: string; address: string }
  | { success: false; error: string };

export type CreateWalletCoreInput = {
  walletSetId: string;
  count?: number;
};

export type CreateWalletInput = StepInput &
  CreateWalletCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: CreateWalletCoreInput,
  credentials: CircleWalletsCredentials
): Promise<CreateWalletResult> {
  if (!input.walletSetId) {
    return { success: false, error: "walletSetId is required" };
  }
  const count = Math.max(1, Number(input.count || 1));
  const result = await circleFetch(credentials, "/v1/w3s/developer/wallets", {
    method: "POST",
    mutating: true,
    idempotencyKey: freshUuid(),
    body: {
      walletSetId: input.walletSetId,
      blockchains: [ARC_TESTNET],
      accountType: "SCA",
      count,
    },
  });
  if (!result.ok) {
    return { success: false, error: result.error };
  }
  const data = asData(result.data);
  const wallets = (data.wallets as Array<Record<string, unknown>>) ?? [];
  const first = wallets[0] ?? data;
  const walletId = String(first.id ?? "");
  const address = String(first.address ?? "");
  if (!walletId) {
    return { success: false, error: "Circle create wallet returned no id" };
  }
  return { success: true, walletId, address };
}

export async function createWalletStep(
  input: CreateWalletInput
): Promise<CreateWalletResult> {
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
