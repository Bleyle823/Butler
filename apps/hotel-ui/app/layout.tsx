export const metadata = {
  title: "Kitchen order",
  description: "Order the honey jar and both jam jars. servebot-1 sets them on the kitchen table.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="en">
      <body style={{ fontFamily: "Georgia, serif", margin: "2rem" }}>{children}</body>
    </html>
  );
}
