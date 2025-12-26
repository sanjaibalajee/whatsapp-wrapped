import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "WhatsApp Wrapped 2025",
  description: "Your year in WhatsApp messages - See your chat statistics and highlights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${plusJakarta.variable} antialiased bg-[#0a0a0a] text-[#ededed]`}
        style={{ fontFamily: "var(--font-jakarta), sans-serif" }}
      >
        {children}
      </body>
    </html>
  );
}
