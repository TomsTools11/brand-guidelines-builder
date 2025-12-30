import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Brand Guidelines Generator",
  description: "Transform any website into a professional brand guidelines PDF using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
