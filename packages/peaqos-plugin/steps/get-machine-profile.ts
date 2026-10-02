import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { machineDid, mcrBase, peaqGetJson } from "../lib/peaq-api";

type Result = { success: true; body: unknown } | { success: false; error: string };

export type GetMachineProfileCoreInput = { machineId: string };
export type GetMachineProfileInput = StepInput &
  GetMachineProfileCoreInput & { integrationId?: string };

async function stepHandler(
  input: GetMachineProfileCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const did = machineDid(input.machineId);
  const result = await peaqGetJson(
    `${mcrBase(credentials)}/machine/${encodeURIComponent(did)}`
  );
  if (!result.ok) {
    return result;
  }
  return { success: true, body: result.data };
}

export async function getMachineProfileStep(input: GetMachineProfileInput): Promise<Result> {
  "use step";
  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};
  return withStepLogging(input, () => stepHandler(input, credentials as PeaqosCredentials));
}

export const _integrationType = "peaqos";
