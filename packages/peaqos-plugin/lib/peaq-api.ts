import "server-only";

import { safeFetch } from "@/lib/safe-fetch";
import type { PeaqosCredentials } from "../credentials";

export const PEAQ_CHAIN_ID = 3338;
export const EVENT_REGISTRY = "0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e";
export const MACHINE_REGISTRY = "0x64b93Cc29b251fAFa83BD110cDB1C24207f85536";
export const MACHINE_SUBSCRIPTION = "0x9e37AD189c334C92e6B8a812Ca4c02f35Ac43895";

export const SUPPORTED_SOURCE_CHAIN_IDS = new Set([0, 3338, 8453, 9990]);

export const EVENT_REGISTRY_ABI = JSON.stringify([
  {
    type: "function",
    name: "submitEvent",
    stateMutability: "nonpayable",
    inputs: [
      { name: "machineId", type: "uint256" },
      { name: "eventType", type: "uint8" },
      { name: "value", type: "uint256" },
      { name: "currency", type: "string" },
      { name: "timestamp", type: "uint256" },
      { name: "dataHash", type: "bytes32" },
      { name: "trustLevel", type: "uint8" },
      { name: "sourceChainId", type: "uint256" },
      { name: "sourceTxHash", type: "bytes32" },
      { name: "metadata", type: "bytes" },
    ],
    outputs: [],
  },
]);

export function mcrBase(credentials: PeaqosCredentials): string {
  return (credentials.PEAQOS_MCR_URL || "https://mcr.peaq.xyz").replace(/\/$/, "");
}

export function verifyBase(credentials: PeaqosCredentials): string {
  return (credentials.PEAQOS_VERIFY_API_URL || "https://mcr.peaq.xyz").replace(
    /\/$/,
    ""
  );
}

export function rpcUrl(credentials: PeaqosCredentials): string {
  return credentials.PEAQOS_RPC_URL || "https://quicknode1.peaq.xyz";
}

export function machineDid(machineId: string): string {
  const trimmed = machineId.trim();
  if (trimmed.startsWith("did:peaq:")) {
    return trimmed;
  }
  return `did:peaq:${trimmed}`;
}

export function validateRevenue(input: {
  value: string;
  currency: string;
  sourceChainId: string;
  trustLevel: string;
}): { ok: true } | { ok: false; error: string } {
  if (!/^\d+$/.test(input.value)) {
    return { ok: false, error: "value must be a minor-unit integer (cents for USD)" };
  }
  if (!/^[A-Z0-9]{3,10}$/.test(input.currency || "USD")) {
    return { ok: false, error: "revenue currency must match ^[A-Z0-9]{3,10}$" };
  }
  const chain = Number(input.sourceChainId);
  if (!SUPPORTED_SOURCE_CHAIN_IDS.has(chain)) {
    return {
      ok: false,
      error: "sourceChainId must be a supported chain ID (0, 3338, 8453, or 9990). Arc 5042002 is not allowed; use 0 and put the Arc hash in rawData.",
    };
  }
  const trust = Number(input.trustLevel);
  if (![0, 1, 2].includes(trust)) {
    return { ok: false, error: "trustLevel must be 0, 1, or 2" };
  }
  if (chain === 0 && trust === 1) {
    return {
      ok: false,
      error: "trustLevel 1 requires a checkable source chain. Use trustLevel 0 with sourceChainId 0.",
    };
  }
  return { ok: true };
}

export async function peaqGetJson(
  url: string
): Promise<{ ok: true; data: unknown } | { ok: false; error: string }> {
  try {
    const response = await safeFetch(url, {
      plugin: "peaqos",
      method: "GET",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, error: `HTTP ${response.status} from ${url}` };
    }
    return { ok: true, data: await response.json() };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
