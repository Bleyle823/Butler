export const metadata = {
  title: "Hotel order",
  description: "Order a pizza for room delivery",
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
