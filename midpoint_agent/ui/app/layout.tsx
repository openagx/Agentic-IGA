import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'midPoint Agent Chat',
  description: 'Chat with midPoint identity management agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}