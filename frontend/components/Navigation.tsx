"use client";

import Link from "next/link";

export default function Navigation() {
  return (
<<<<<<< HEAD
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto">
        <div className="flex space-x-4">
          <Link
            href="/"
            className="text-white hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
          >
            Home
          </Link>
          <Link
            href="/files"
            className="text-white hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
          >
            Files
          </Link>
=======
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-xl font-bold text-primary">
                Data Description Quality Tool
              </span>
            </Link>
          </div>

          <div className="flex items-center space-x-8">
            <Link
              href="/"
              className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
            >
              Home
            </Link>
            <Link
              href="/file-management"
              className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
            >
              File Management
            </Link>
          </div>
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
        </div>
      </div>
    </nav>
  );
}
