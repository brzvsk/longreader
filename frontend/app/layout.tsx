import type { Metadata } from "next";
import { Inter } from 'next/font/google'
import "./globals.css"
import { AuthProvider } from '@/components/providers/auth-provider';
import { RequireAuth } from '@/components/auth/require-auth';
import { TelegramProvider } from '@/components/providers/telegram-provider';
import { DeepLinkHandler } from '@/components/providers/deep-link-handler';

const inter = Inter({ subsets: ['latin', 'cyrillic'] })

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
    <html lang="en" suppressHydrationWarning>
      <head>
        <script 
          src="https://telegram.org/js/telegram-web-app.js?56" 
          async={false}
        />
      </head>
      <body className={`${inter.className} font-sans antialiased`}>
        <AuthProvider>
          <RequireAuth>
            <TelegramProvider>
              <DeepLinkHandler>
                {children}
              </DeepLinkHandler>
            </TelegramProvider>
          </RequireAuth>
        </AuthProvider>
      </body>
    </html>
  );
}
