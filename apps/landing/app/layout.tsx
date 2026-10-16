import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Butler — Paid when the table is set",
  description:
    "servebot-1 runs the kitchen job. Circle holds USDC on Arc. peaq records pickup and delivery.",
};

export const viewport: Viewport = {
  themeColor: "#F7F5F0",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
