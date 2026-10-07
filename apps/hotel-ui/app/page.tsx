"use client";

import { useState } from "react";

const ROOMS = ["room-1204", "room-1205", "room-1206"];
const ITEMS = ["honey jar", "jam jar 1", "jam jar 2"];

export default function OrderPage(): React.ReactElement {
  const [room, setRoom] = useState("room-1204");
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setPending(true);
    setMessage("");
    try {
      const response = await fetch("/api/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room, items: ITEMS }),
      });
      const body = (await response.json()) as { error?: string; jobId?: string };
      if (!response.ok) {
        setMessage(body.error || "Order failed");
        return;
      }
      setMessage(`Order sent. Job ${body.jobId || ""}`.trim());
    } catch {
      setMessage("Could not reach the hotel service");
    } finally {
      setPending(false);
    }
  }

  return (
    <main>
      <h1>Kitchen order</h1>
      <p>
        servebot-1 brings the honey jar, then jam jar 1 and jam jar 2, onto the kitchen table.
        The set is 6.00 USDC. The room is who ordered. The robot starts that run only after
        the deposit is on the bridge.
      </p>
      <ul>
        {ITEMS.map((name) => (
          <li key={name}>{name}</li>
        ))}
      </ul>
      <form onSubmit={submit}>
        <label htmlFor="room">Who ordered</label>
        <div>
          <select id="room" value={room} onChange={(event) => setRoom(event.target.value)}>
            {ROOMS.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <button disabled={pending} type="submit">
          {pending ? "Sending" : "Order the jars"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
    </main>
  );
}
