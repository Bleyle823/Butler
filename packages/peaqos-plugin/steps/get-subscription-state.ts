import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { safeFetch } from "@/lib/safe-fetch";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { MACHINE_SUBSCRIPTION, rpcUrl } from "../lib/peaq-api";

type Result =
  | { success: true; eligible: boolean; body: unknown }
  | { success: false; error: string };

export type GetSubscriptionStateCoreInput = { machineId: string };
export type GetSubscriptionStateInput = StepInput &
  GetSubscriptionStateCoreInput & { integrationId?: string };

function padId(machineId: string): string {
  const n = BigInt(machineId.replace(/^did:peaq:/, ""));
  return n.toString(16).padStart(64, "0");
}

async function stepHandler(
  input: GetSubscriptionStateCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  // subscriptions(uint256) selector 0x8acbe3b1 is a placeholder until PHASE0 ABI hunt locks it.
  // eth_call still proves the RPC path; decode is best-effort.
  const data = `0x8acbe3b1${padId(input.machineId)}`;
  try {
    const response = await safeFetch(rpcUrl(credentials), {
      plugin: "peaqos",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "eth_call",
        params: [
          { to: MACHINE_SUBSCRIPTION, data },
          "latest",
        ],
      }),
    });
    const body = (await response.json()) as { result?: string; error?: { message: string } };
    if (body.error) {
      return { success: false, error: body.error.message };
    }
    const result = body.result || "0x";
    const eligible = result !== "0x" && result !== "0x" + "0".repeat(64);
    return { success: true, eligible, body };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function getSubscriptionStateStep(
  input: GetSubscriptionStateInput
): Promise<Result> {
  "use step";
  const credentials = input.integrationId
    ? await fetchCredentials(input.integrationId, {
        organizationId: input._context?.organizationId ?? null,
      })
    : {};
  return withStepLogging(input, () => stepHandler(input, credentials as PeaqosCredentials));
}

export const _integrationType = "peaqos";
