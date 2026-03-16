import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bunuelos Pulse | Monitoring Hub",
  description: "Real-time monitoring for Bunuelos SAS Data Pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
