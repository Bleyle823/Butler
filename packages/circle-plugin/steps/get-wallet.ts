import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { asData, circleFetch } from "../lib/circle-api";

type GetWalletResult =
  | { success: true; walletId: string; address: string }
  | { success: false; error: string };

export type GetWalletCoreInput = {
  walletId: string;
};

export type GetWalletInput = StepInput &
  GetWalletCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: GetWalletCoreInput,
  credentials: CircleWalletsCredentials
): Promise<GetWalletResult> {
  if (!input.walletId) {
    return { success: false, error: "walletId is required" };
  }
  const result = await circleFetch(
    credentials,
    `/v1/w3s/developer/wallets/${encodeURIComponent(input.walletId)}`,
    { method: "GET" }
  );
  if (!result.ok) {
    return { success: false, error: result.error };
  }
  const data = asData(result.data);
  const wallet = (data.wallet as Record<string, unknown> | undefined) ?? data;
  return {
    success: true,
    walletId: String(wallet.id ?? input.walletId),
    address: String(wallet.address ?? ""),
  };
}

export async function getWalletStep(
  input: GetWalletInput
): Promise<GetWalletResult> {
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
