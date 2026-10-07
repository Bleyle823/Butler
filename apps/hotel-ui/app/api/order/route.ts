import { randomBytes } from "node:crypto";

export async function POST(request: Request): Promise<Response> {
  const settler = process.env.BUTLER_SETTLER_URL || "http://127.0.0.1:8788";

  const kitchen = ["honey jar", "jam jar 1", "jam jar 2"];
  let body: { room?: string; items?: string[] };
  try {
    body = (await request.json()) as { room?: string; items?: string[] };
  } catch {
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const room = body.room || "";
  if (!["room-1204", "room-1205", "room-1206"].includes(room)) {
    return Response.json({ error: "Unknown room" }, { status: 400 });
  }
  const items = Array.isArray(body.items) ? body.items : [];
  if (items.length !== kitchen.length || items.some((name, index) => name !== kitchen[index])) {
    return Response.json(
      { error: "Order is honey jar, jam jar 1, and jam jar 2" },
      { status: 400 }
    );
  }

  const jobId = `0x${randomBytes(32).toString("hex")}`;
  const configuredMachine = process.env.PEAQ_MACHINE_ID || "";
  const machineId = /^0x[0-9a-fA-F]{64}$/.test(configuredMachine)
    ? configuredMachine
    : `0x${"0".repeat(64)}`;
  const secret = process.env.BUTLER_SECRET || "change-me";
  let upstream: Response;
  try {
    upstream = await fetch(`${settler.replace(/\/$/, "")}/order`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Butler-Secret": secret,
      },
      body: JSON.stringify({
        jobId,
        room,
        items: kitchen,
        machineId,
      }),
    });
  } catch {
    return Response.json(
      { error: "Settler is not answering. Start packages/settler first." },
      { status: 503 }
    );
  }

  if (!upstream.ok) {
    let detail = `Settler returned ${upstream.status}`;
    try {
      const failed = (await upstream.json()) as { error?: string };
      if (failed.error) {
        detail = failed.error;
      }
    } catch {
      detail = `Settler returned ${upstream.status}`;
    }
    return Response.json({ error: detail }, { status: 502 });
  }

  return Response.json({ jobId, room, items: kitchen });
}
