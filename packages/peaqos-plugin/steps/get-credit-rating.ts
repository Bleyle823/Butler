import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { machineDid, mcrBase, peaqGetJson } from "../lib/peaq-api";

type Result =
  | { success: true; rating: string; score: string; body: unknown }
  | { success: false; error: string };

export type GetCreditRatingCoreInput = { machineId: string };
export type GetCreditRatingInput = StepInput &
  GetCreditRatingCoreInput & { integrationId?: string };

async function stepHandler(
  input: GetCreditRatingCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const did = machineDid(input.machineId);
  const result = await peaqGetJson(`${mcrBase(credentials)}/mcr/${encodeURIComponent(did)}`);
  if (!result.ok) {
    return result;
  }
  const body = result.data as Record<string, unknown>;
  return {
    success: true,
    rating: String(body.rating ?? body.letter ?? ""),
    score: String(body.score ?? body.mcr ?? ""),
    body,
  };
}

export async function getCreditRatingStep(input: GetCreditRatingInput): Promise<Result> {
  "use step";
  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};
  return withStepLogging(input, () => stepHandler(input, credentials as PeaqosCredentials));
}

export const _integrationType = "peaqos";
