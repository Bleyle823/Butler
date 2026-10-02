import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { peaqGetJson, verifyBase } from "../lib/peaq-api";

type Result =
  | { success: true; chipStatus: string; kybStatus: string; body: unknown }
  | { success: false; error: string };

export type GetVerificationCoreInput = { machineId: string };
export type GetVerificationInput = StepInput &
  GetVerificationCoreInput & { integrationId?: string };

async function stepHandler(
  input: GetVerificationCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const base = verifyBase(credentials);
  const result = await peaqGetJson(
    `${base}/v1/verify/machines/${encodeURIComponent(input.machineId)}`
  );
  if (!result.ok) {
    return result;
  }
  const body = result.data as Record<string, unknown>;
  const verification = (body.verification as Record<string, unknown> | undefined) ?? {};
  const chip = (verification.chip as Record<string, unknown> | undefined) ?? {};
  const kyb = (verification.kyb as Record<string, unknown> | undefined) ?? {};
  return {
    success: true,
    chipStatus: String(chip.status ?? "unverified"),
    kybStatus: String(kyb.status ?? "unverified"),
    body,
  };
}

export async function getVerificationStep(input: GetVerificationInput): Promise<Result> {
  "use step";
  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};
  return withStepLogging(input, () => stepHandler(input, credentials as PeaqosCredentials));
}

export const _integrationType = "peaqos";
