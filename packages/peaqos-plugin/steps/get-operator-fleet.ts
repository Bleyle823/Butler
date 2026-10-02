import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { mcrBase, peaqGetJson } from "../lib/peaq-api";

type Result = { success: true; body: unknown } | { success: false; error: string };

export type GetOperatorFleetCoreInput = { operatorDid: string };
export type GetOperatorFleetInput = StepInput &
  GetOperatorFleetCoreInput & { integrationId?: string };

async function stepHandler(
  input: GetOperatorFleetCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.operatorDid) {
    return { success: false, error: "operatorDid is required" };
  }
  const did = input.operatorDid.startsWith("did:")
    ? input.operatorDid
    : `did:peaq:${input.operatorDid}`;
  const result = await peaqGetJson(
    `${mcrBase(credentials)}/operator/${encodeURIComponent(did)}/machines`
  );
  if (!result.ok) {
    return result;
  }
  return { success: true, body: result.data };
}

export async function getOperatorFleetStep(input: GetOperatorFleetInput): Promise<Result> {
  "use step";
  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};
  return withStepLogging(input, () => stepHandler(input, credentials as PeaqosCredentials));
}

export const _integrationType = "peaqos";
