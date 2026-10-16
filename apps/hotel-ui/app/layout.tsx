import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kitchen order — Butler",
  description:
    "Order the heineken beer, beverage can, and water bottle. servebot-1 sets them on the kitchen table.",
};

export const viewport: Viewport = {
  themeColor: "#F7F5F0",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
