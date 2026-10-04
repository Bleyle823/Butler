import "server-only";

import { keccak256, toBytes } from "viem";
import { writeContractCore } from "@/plugins/web3/steps/write-contract-core";
import type { StepInput } from "@/lib/workflow/executor/step-handler";
import {
  EVENT_REGISTRY,
  EVENT_REGISTRY_ABI,
  MACHINE_REGISTRY,
  MACHINE_SUBSCRIPTION,
} from "./peaq-api";

const PEAQ_NETWORK = "3338";

const SUBSCRIPTION_ABI = JSON.stringify([
  {
    type: "function",
    name: "renew",
    stateMutability: "nonpayable",
    inputs: [{ name: "machineId", type: "uint256" }],
    outputs: [],
  },
]);

const REGISTRY_ABI = JSON.stringify([
  {
    type: "function",
    name: "suspend",
    stateMutability: "nonpayable",
    inputs: [{ name: "machineId", type: "uint256" }],
    outputs: [],
  },
  {
    type: "function",
    name: "resume",
    stateMutability: "nonpayable",
    inputs: [{ name: "machineId", type: "uint256" }],
    outputs: [],
  },
]);

export async function submitEventWrite(
  input: StepInput & {
    machineId: string;
    eventType: number;
    value: string;
    rawData: string;
    trustLevel: string;
    sourceChainId: string;
    sourceTxHash: string;
    currency: string;
  }
) {
  const timestamp = Math.floor(Date.now() / 1000) - 30;
  const dataHash = keccak256(toBytes(input.rawData || ""));
  const hash = input.sourceTxHash?.startsWith("0x")
    ? input.sourceTxHash
    : `0x${(input.sourceTxHash || "0").padStart(64, "0")}`;

  return writeContractCore({
    ...input,
    contractAddress: EVENT_REGISTRY,
    network: PEAQ_NETWORK,
    abi: EVENT_REGISTRY_ABI,
    abiFunction: "submitEvent",
    functionArgs: [
      input.machineId,
      input.eventType,
      input.value,
      input.currency,
      timestamp,
      dataHash,
      Number(input.trustLevel),
      Number(input.sourceChainId),
      hash,
      "0x",
    ],
  });
}

export async function subscriptionWrite(
  input: StepInput & { machineId: string },
  fn: "renew" | "suspend" | "resume"
) {
  if (fn === "renew") {
    return writeContractCore({
      ...input,
      contractAddress: MACHINE_SUBSCRIPTION,
      network: PEAQ_NETWORK,
      abi: SUBSCRIPTION_ABI,
      abiFunction: "renew",
      functionArgs: [input.machineId],
    });
  }
  return writeContractCore({
    ...input,
    contractAddress: MACHINE_REGISTRY,
    network: PEAQ_NETWORK,
    abi: REGISTRY_ABI,
    abiFunction: fn,
    functionArgs: [input.machineId],
  });
}
