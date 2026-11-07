import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Msaidizi — AI Customer Support",
  description: "Your intelligent customer support workspace."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
