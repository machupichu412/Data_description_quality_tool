"use client";

import Link from "next/link";

export default function Navigation() {
  return (
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
        </div>
      </div>
    </nav>
  );
}
