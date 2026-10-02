import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { USDC_ARC, asData, circleFetch } from "../lib/circle-api";

type GetUsdcBalanceResult =
  | { success: true; amount: string }
  | { success: false; error: string };

export type GetUsdcBalanceCoreInput = {
  walletId: string;
};

export type GetUsdcBalanceInput = StepInput &
  GetUsdcBalanceCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: GetUsdcBalanceCoreInput,
  credentials: CircleWalletsCredentials
): Promise<GetUsdcBalanceResult> {
  if (!input.walletId) {
    return { success: false, error: "walletId is required" };
  }
  const result = await circleFetch(
    credentials,
    `/v1/w3s/developer/wallets/${encodeURIComponent(input.walletId)}/balances`,
    { method: "GET" }
  );
  if (!result.ok) {
    return { success: false, error: result.error };
  }
  const data = asData(result.data);
  const tokenBalances = (data.tokenBalances as Array<Record<string, unknown>>) ?? [];
  const usdc = tokenBalances.find((row) => {
    const token = (row.token as Record<string, unknown> | undefined) ?? {};
    const symbol = String(token.symbol ?? row.symbol ?? "").toUpperCase();
    const address = String(token.tokenAddress ?? row.tokenAddress ?? "").toLowerCase();
    return symbol === "USDC" || address === USDC_ARC.toLowerCase();
  });
  const amount = String(usdc?.amount ?? "0");
  return { success: true, amount };
}

export async function getUsdcBalanceStep(
  input: GetUsdcBalanceInput
): Promise<GetUsdcBalanceResult> {
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
