import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";
import SmoothScrolling from "@/components/SmoothScrolling";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "400", "500", "600"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  weight: ["300", "400", "500", "700"],
});

export const metadata: Metadata = {
  title: "PRISM — Lunar South Pole Ice Detection & Mission Planning",
  description:
    "Planetary Radar Ice-Scout Mission system. Radar-based detection of potential water ice candidates in lunar permanently shadowed regions. Chandrayaan-2 DFSAR analysis.",
  keywords: ["lunar", "ice detection", "DFSAR", "Chandrayaan-2", "south pole", "PSR", "radar"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
        style={{
          fontFamily: "var(--font-inter), ui-sans-serif, system-ui, sans-serif",
        }}
      >
        <SmoothScrolling>
          <Nav />
          {children}
        </SmoothScrolling>
      </body>
    </html>
  );
}
