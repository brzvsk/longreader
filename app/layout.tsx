import type { Metadata } from "next";
import { Inter, Roboto, Open_Sans } from 'next/font/google'
import "./globals.css";

// For a single font
const inter = Inter({ subsets: ['latin', 'cyrillic'] })

// For variable fonts
const roboto = Roboto({
  weight: ['400', '500', '700'],
  subsets: ['latin', 'cyrillic'],
  display: 'swap',
})

// Multiple weights and styles
const openSans = Open_Sans({
  subsets: ['latin', 'cyrillic'],
  weight: ['300', '400', '600', '700'],
  style: ['normal', 'italic']
})

export const metadata: Metadata = {
  title: "Longreader",
  description: "Save and read long form content.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
