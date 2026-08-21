import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { TopNav } from "@/components/layout/TopNav";
import { Footer } from "@/components/layout/Footer";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  weight: ["400", "500", "600"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PRISM MISSION CONTROL - Dashboard",
  description: "Lunar South Polar Subsurface Ice Detection, Surface Hazard Characterization, Landing Site Selection, and Rover Traverse Planning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${ibmPlexMono.variable} h-full antialiased light`}
    >
      <body className="bg-background font-body-md text-on-background h-screen flex flex-col overflow-hidden">
        <TopNav />
        {children}
        <Footer />
      </body>
    </html>
  );
}
