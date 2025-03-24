import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Data Description Quality Tool',
  description: 'A tool to evaluate the quality of data descriptions using LLM',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen">
          <header className="bg-primary text-white p-4">
            <div className="container mx-auto">
              <h1 className="text-2xl font-bold">Data Description Quality Tool</h1>
            </div>
          </header>
          <main className="container mx-auto p-4">
            {children}
          </main>
          <footer className="bg-secondary text-white p-4 mt-8">
            <div className="container mx-auto text-center">
              <p>© {new Date().getFullYear()} Data Description Quality Tool</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
