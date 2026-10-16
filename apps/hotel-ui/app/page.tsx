"use client";

import { useState } from "react";
import ButtonGradient from "../assets/svg/ButtonGradient";
import { check2, curve, robot } from "../assets";
import Button from "../components/Button";
import Footer from "../components/Footer";
import Heading from "../components/Heading";
import OrderHeader from "../components/OrderHeader";
import Section from "../components/Section";

const ROOMS = ["room-1204", "room-1205", "room-1206"];
const ITEMS = ["heineken beer", "beverage can", "water bottle"];

export default function OrderPage(): React.ReactElement {
  const [room, setRoom] = useState("room-1204");
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  const [isError, setIsError] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setPending(true);
    setMessage("");
    setIsError(false);
    try {
      const response = await fetch("/api/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room, items: ITEMS }),
      });
      const body = (await response.json()) as { error?: string; jobId?: string };
      if (!response.ok) {
        setMessage(body.error || "Order failed");
        setIsError(true);
        return;
      }
      setMessage(`Order sent. Job ${body.jobId || ""}`.trim());
      setIsError(false);
    } catch {
      setMessage("Could not reach the hotel service");
      setIsError(true);
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      <div className="min-h-screen bg-n-8 pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden">
        <OrderHeader />

        <Section
          className="pt-[8rem] -mt-[5.25rem] overflow-hidden"
          crosses
          crossesOffset="lg:translate-y-[5.25rem]"
          customPaddings
          id="order"
        >
          <div className="container relative">
            <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-12 md:mb-16 lg:mb-20">
              <h1 className="h1 mb-6">
                Drinks to the{" "}
                <span className="inline-block relative">
                  kitchen table.{" "}
                  <img
                    src={curve}
                    className="absolute top-full left-0 w-full xl:-mt-2"
                    width={624}
                    height={28}
                    alt=""
                  />
                </span>
              </h1>
              <p className="body-1 max-w-3xl mx-auto text-n-2">
                servebot-1 brings the heineken beer, then the beverage can and the water bottle,
                onto the kitchen table. The set is 6.00 USDC. The room is who ordered. The robot
                starts that run only after the deposit is on the bridge.
              </p>
            </div>

            <div className="relative z-1 grid gap-10 lg:grid-cols-2 lg:gap-12 xl:gap-16 items-start max-w-5xl mx-auto">
              <div className="relative p-0.5 rounded-3xl bg-edge overflow-hidden">
                <div className="relative bg-n-8 rounded-[1.375rem] p-6 md:p-8 lg:p-10">
                  <Heading
                    className="!mb-8 !max-w-none text-left md:!text-left"
                    tag="Place order"
                    title="Drinks to the kitchen table"
                    text="Fixed bundle for the demo. Circle holds payment until delivery is recorded."
                  />

                  <ul className="space-y-4 mb-6">
                    {ITEMS.map((name) => (
                      <li
                        key={name}
                        className="flex items-center gap-3 body-2 text-n-2 capitalize"
                      >
                        <img src={check2} width={24} height={24} alt="" />
                        {name}
                      </li>
                    ))}
                  </ul>

                  <p className="font-code text-sm font-semibold text-n-1 mb-8">
                    6.00 USDC
                  </p>

                  <form onSubmit={submit} className="space-y-6">
                    <div>
                      <label
                        htmlFor="room"
                        className="tagline block mb-3 text-n-3"
                      >
                        Who ordered
                      </label>
                      <select
                        id="room"
                        value={room}
                        onChange={(event) => setRoom(event.target.value)}
                        className="w-full font-code text-sm bg-n-7 border border-stroke-1 rounded-2xl px-4 py-3 text-n-1 outline-none focus:border-edge transition-colors"
                      >
                        {ROOMS.map((name) => (
                          <option key={name} value={name}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <Button
                      white
                      type="submit"
                      disabled={pending}
                      className="w-full sm:w-auto"
                    >
                      {pending ? "Sending…" : "Order the drinks"}
                    </Button>
                  </form>

                  {message ? (
                    <div
                      className={`mt-8 p-4 bg-n-7/90 backdrop-blur border rounded-2xl ${
                        isError ? "border-red-400/40" : "border-edge/30"
                      }`}
                      role="status"
                    >
                      <p
                        className={`body-2 ${isError ? "text-n-1" : "text-n-2"}`}
                      >
                        {message}
                      </p>
                    </div>
                  ) : null}
                </div>
              </div>

              <div className="relative p-0.5 rounded-3xl bg-edge overflow-hidden lg:sticky lg:top-28">
                <div className="relative bg-n-8 rounded-[1.375rem] overflow-hidden">
                  <div className="h-[1.4rem] bg-n-10 rounded-t-[1.25rem]" />
                  <div className="aspect-[33/40] rounded-b-[1.25rem] overflow-hidden md:aspect-[688/490]">
                    <img
                      src={robot}
                      className="w-full scale-[1.7] translate-y-[8%] md:scale-[1] md:-translate-y-[10%]"
                      width={1024}
                      height={490}
                      alt="servebot-1 in the hotel kitchen simulation"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Section>

        <Footer />
      </div>

      <ButtonGradient />
    </>
  );
}
