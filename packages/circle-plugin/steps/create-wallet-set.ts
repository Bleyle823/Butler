import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { CircleWalletsCredentials } from "../credentials";
import { asData, circleFetch, freshUuid } from "../lib/circle-api";

type CreateWalletSetResult =
  | { success: true; walletSetId: string }
  | { success: false; error: string };

export type CreateWalletSetCoreInput = {
  name: string;
};

export type CreateWalletSetInput = StepInput &
  CreateWalletSetCoreInput & {
    integrationId?: string;
  };

async function stepHandler(
  input: CreateWalletSetCoreInput,
  credentials: CircleWalletsCredentials
): Promise<CreateWalletSetResult> {
  if (!input.name) {
    return { success: false, error: "name is required" };
  }
  const result = await circleFetch(
    credentials,
    "/v1/w3s/developer/walletSets",
    {
      method: "POST",
      mutating: true,
      idempotencyKey: freshUuid(),
      body: { name: input.name },
    }
  );
  if (!result.ok) {
    return { success: false, error: result.error };
  }
  const data = asData(result.data);
  const walletSet = (data.walletSet as Record<string, unknown> | undefined) ?? data;
  const id = String(walletSet.id ?? "");
  if (!id) {
    return { success: false, error: "Circle wallet set returned no id" };
  }
  return { success: true, walletSetId: id };
}

export async function createWalletSetStep(
  input: CreateWalletSetInput
): Promise<CreateWalletSetResult> {
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
