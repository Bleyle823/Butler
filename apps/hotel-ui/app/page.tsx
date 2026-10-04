"use client";

import { useState } from "react";

const ROOMS = ["room-1204", "room-1205", "room-1206"];

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
        body: JSON.stringify({ room, item: "pizza" }),
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
      <h1>Room service</h1>
      <p>Pizza is 6.00 USDC. The robot moves only after the order is accepted.</p>
      <form onSubmit={submit}>
        <label htmlFor="room">Room</label>
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
          {pending ? "Sending" : "Order pizza"}
        </button>
      </form>
      {message ? <p>{message}</p> : null}
    </main>
  );
}
