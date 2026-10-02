import "server-only";

import { randomUUID, publicEncrypt, constants } from "node:crypto";
import { safeFetch } from "@/lib/safe-fetch";
import type { CircleWalletsCredentials } from "../credentials";

export const ARC_TESTNET = "ARC-TESTNET";
export const USDC_ARC = "0x3600000000000000000000000000000000000000";

const HOSTS: Record<string, string> = {
  sandbox: "https://api-sandbox.circle.com",
  production: "https://api.circle.com",
};

export function circleBaseUrl(credentials: CircleWalletsCredentials): string {
  const env = (credentials.CIRCLE_ENV || "sandbox").toLowerCase();
  return HOSTS[env] ?? HOSTS.sandbox;
}

export function requireApiKey(
  credentials: CircleWalletsCredentials
): { ok: true; apiKey: string } | { ok: false; error: string } {
  const apiKey = credentials.CIRCLE_API_KEY;
  if (!apiKey) {
    return {
      ok: false,
      error:
        "CIRCLE_API_KEY is not configured. Add it in Project Integrations.",
    };
  }
  return { ok: true, apiKey };
}

function requireEntitySecret(
  credentials: CircleWalletsCredentials
): { ok: true; secret: string } | { ok: false; error: string } {
  const secret = credentials.CIRCLE_ENTITY_SECRET;
  if (!secret) {
    return {
      ok: false,
      error:
        "CIRCLE_ENTITY_SECRET is not configured. Register it in Circle Console and add it in Project Integrations. Never log this value.",
    };
  }
  if (!/^[0-9a-fA-F]{64}$/.test(secret)) {
    return {
      ok: false,
      error: "CIRCLE_ENTITY_SECRET must be 32-byte hex (64 characters).",
    };
  }
  return { ok: true, secret };
}

async function getEntityPublicKey(apiKey: string, base: string): Promise<string> {
  const response = await safeFetch(`${base}/v1/w3s/config/entity/publicKey`, {
    plugin: "circle-wallets",
    method: "GET",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Circle publicKey HTTP ${response.status}`);
  }
  const body = (await response.json()) as { data?: { publicKey?: string } };
  const pem = body.data?.publicKey;
  if (!pem) {
    throw new Error("Circle publicKey response missing data.publicKey");
  }
  return pem;
}

export async function entitySecretCiphertext(
  credentials: CircleWalletsCredentials,
  apiKey: string,
  base: string
): Promise<{ ok: true; ciphertext: string } | { ok: false; error: string }> {
  const secret = requireEntitySecret(credentials);
  if (!secret.ok) {
    return secret;
  }
  try {
    const pem = await getEntityPublicKey(apiKey, base);
    const encrypted = publicEncrypt(
      {
        key: pem,
        padding: constants.RSA_PKCS1_OAEP_PADDING,
        oaepHash: "sha256",
      },
      Buffer.from(secret.secret, "utf8")
    );
    return { ok: true, ciphertext: encrypted.toString("base64") };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export function deriveIdempotencyKey(jobId: string, stepName: string): string {
  const raw = `${jobId}:${stepName}`;
  if (/^[0-9a-fA-F-]{36}$/.test(jobId)) {
    return jobId;
  }
  // Circle wants a UUID. Derive a stable UUID v5-like from job + step without extra deps.
  const hex = Buffer.from(raw).toString("hex").padEnd(32, "0").slice(0, 32);
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-5${hex.slice(13, 16)}-a${hex.slice(17, 20)}-${hex.slice(20, 32)}`;
}

export function freshUuid(): string {
  return randomUUID();
}

export async function circleFetch(
  credentials: CircleWalletsCredentials,
  path: string,
  init: {
    method: string;
    body?: unknown;
    mutating?: boolean;
    idempotencyKey?: string;
  }
): Promise<{ ok: true; data: unknown; status: number } | { ok: false; error: string; status?: number }> {
  const key = requireApiKey(credentials);
  if (!key.ok) {
    return key;
  }
  const base = circleBaseUrl(credentials);
  const headers: Record<string, string> = {
    Authorization: `Bearer ${key.apiKey}`,
    Accept: "application/json",
  };

  let body: string | undefined;
  if (init.body !== undefined) {
    headers["Content-Type"] = "application/json";
    const payload = { ...(init.body as Record<string, unknown>) };
    if (init.mutating) {
      const cipher = await entitySecretCiphertext(credentials, key.apiKey, base);
      if (!cipher.ok) {
        return cipher;
      }
      payload.entitySecretCiphertext = cipher.ciphertext;
      payload.idempotencyKey = init.idempotencyKey ?? freshUuid();
    }
    body = JSON.stringify(payload);
  }

  try {
    const response = await safeFetch(`${base}${path}`, {
      plugin: "circle-wallets",
      method: init.method,
      headers,
      body,
    });
    const text = await response.text();
    let parsed: unknown = text;
    try {
      parsed = text ? JSON.parse(text) : {};
    } catch {
      parsed = { raw: text };
    }
    if (!response.ok) {
      const err = parsed as { message?: string; code?: number };
      return {
        ok: false,
        error: err.message || `Circle HTTP ${response.status}`,
        status: response.status,
      };
    }
    return { ok: true, data: parsed, status: response.status };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export function asData(payload: unknown): Record<string, unknown> {
  if (payload && typeof payload === "object" && "data" in payload) {
    const data = (payload as { data: unknown }).data;
    if (data && typeof data === "object") {
      return data as Record<string, unknown>;
    }
  }
  return (payload as Record<string, unknown>) ?? {};
}
