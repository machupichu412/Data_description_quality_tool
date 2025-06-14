import "./globals.css";
<<<<<<< HEAD
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navigation from "@/components/Navigation";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Data Description Quality Tool",
  description: "A tool to evaluate the quality of data descriptions using LLM",
=======
import "./custom-font.css";
import type { Metadata } from "next";
import Navigation from "../components/Navigation";

export const metadata: Metadata = {
  title: "Data Description Quality Tool",
  description: "Evaluate the quality of data descriptions",
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
<<<<<<< HEAD
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <header className="bg-primary text-white p-4">
            <div className="container mx-auto">
              <h1 className="text-2xl font-bold">
                Data Description Quality Tool
              </h1>
            </div>
          </header>
          <Navigation />
          <main className="flex-grow container mx-auto p-4">{children}</main>
          <footer className="bg-secondary text-white p-4">
            <div className="container mx-auto text-center">
              <p> {new Date().getFullYear()} Data Description Quality Tool</p>
            </div>
          </footer>
        </div>
=======
      <body>
        <Navigation />
        <main className="min-h-screen p-6">{children}</main>
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
      </body>
    </html>
  );
}
