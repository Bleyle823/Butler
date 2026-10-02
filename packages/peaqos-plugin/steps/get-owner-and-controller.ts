import "server-only";

import { fetchCredentials } from "@/lib/credential-fetcher";
import { safeFetch } from "@/lib/safe-fetch";
import { type StepInput, withStepLogging } from "@/lib/workflow/executor/step-handler";
import type { PeaqosCredentials } from "../credentials";
import { MACHINE_REGISTRY, rpcUrl } from "../lib/peaq-api";

type Result =
  | { success: true; owner: string; controller: string }
  | { success: false; error: string };

export type GetOwnerAndControllerCoreInput = { machineId: string };
export type GetOwnerAndControllerInput = StepInput &
  GetOwnerAndControllerCoreInput & { integrationId?: string };

function padId(machineId: string): string {
  const n = BigInt(machineId.replace(/^did:peaq:/, ""));
  return n.toString(16).padStart(64, "0");
}

function addressFromWord(word: string): string {
  const hex = word.replace(/^0x/, "").padStart(64, "0");
  return "0x" + hex.slice(24);
}

async function ethCall(rpc: string, data: string): Promise<string> {
  const response = await safeFetch(rpc, {
    plugin: "peaqos",
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_call",
      params: [{ to: MACHINE_REGISTRY, data }, "latest"],
    }),
  });
  const body = (await response.json()) as { result?: string; error?: { message: string } };
  if (body.error) {
    throw new Error(body.error.message);
  }
  return body.result || "0x";
}

async function stepHandler(
  input: GetOwnerAndControllerCoreInput,
  credentials: PeaqosCredentials
): Promise<Result> {
  if (!input.machineId) {
    return { success: false, error: "machineId is required" };
  }
  const id = padId(input.machineId);
  const rpc = rpcUrl(credentials);
  try {
    const ownerWord = await ethCall(rpc, `0x6352211e${id}`);
    // controllerOf(uint256) — confirm selector in PHASE0 ABI hunt
    const controllerWord = await ethCall(rpc, `0xb66a0e5d${id}`);
    return {
      success: true,
      owner: addressFromWord(ownerWord),
      controller: addressFromWord(controllerWord),
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function getOwnerAndControllerStep(
  input: GetOwnerAndControllerInput
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
