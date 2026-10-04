import { randomBytes } from "node:crypto";

export async function POST(request: Request): Promise<Response> {
  const webhook = process.env.KEEPERHUB_DISPATCH_WEBHOOK || "";
  if (!webhook) {
    return Response.json(
      { error: "KEEPERHUB_DISPATCH_WEBHOOK is not set. Import the dispatch workflow and paste its webhook URL." },
      { status: 503 }
    );
  }

  let body: { room?: string; item?: string };
  try {
    body = (await request.json()) as { room?: string; item?: string };
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const room = body.room || "";
  if (!["room-1204", "room-1205", "room-1206"].includes(room)) {
    return Response.json({ error: "Unknown room" }, { status: 400 });
  }
  if (body.item !== "pizza") {
    return Response.json({ error: "Only pizza is on the menu" }, { status: 400 });
  }

  const jobId = `0x${randomBytes(32).toString("hex")}`;
  const configuredMachine = process.env.PEAQ_MACHINE_ID || "";
  const machineId = /^0x[0-9a-fA-F]{64}$/.test(configuredMachine)
    ? configuredMachine
    : `0x${"0".repeat(64)}`;
  const webhookKey = process.env.KEEPERHUB_WEBHOOK_KEY || "";
  const upstream = await fetch(webhook, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(webhookKey ? { Authorization: `Bearer ${webhookKey}` } : {}),
    },
    body: JSON.stringify({
      jobId,
      room,
      item: "pizza",
      machineId,
    }),
  });

  if (!upstream.ok) {
    return Response.json(
      { error: `Dispatch webhook returned ${upstream.status}` },
      { status: 502 }
    );
  }

  return Response.json({ jobId, room });
}
