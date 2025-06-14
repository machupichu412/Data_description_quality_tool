"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { FileRecord } from "../../components/FileHistory";

export default function FileManagement() {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get("http://localhost:5005/api/files");
      setFiles(response.data.files || []);
      setError(null);
    } catch (error) {
      console.error("Error fetching files:", error);
      setError("Failed to fetch files");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (fileId: number) => {
    if (
      !confirm(
        "Are you sure you want to delete this file and its descriptions?"
      )
    ) {
      return;
    }

    try {
      await axios.delete(`http://localhost:5005/api/files/${fileId}`);
      setFiles(files.filter((file) => file.id !== fileId));
    } catch (error) {
      console.error("Error deleting file:", error);
      setError("Failed to delete file");
    }
  };

  const handleDownloadOriginal = async (fileId: number, filename: string) => {
    try {
      const response = await axios.get(
        `http://localhost:5005/api/files/${fileId}/download`,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading original file:", error);
      setError("Failed to download original file");
    }
  };

  const handleDownloadProcessed = async (fileId: number) => {
    try {
      const response = await axios.get(
        `http://localhost:5005/api/files/${fileId}/descriptions/download`,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `processed_descriptions_${fileId}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading processed descriptions:", error);
      setError("Failed to download processed descriptions");
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">File Management</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}

      <button
        onClick={fetchFiles}
        className="mb-6 bg-primary text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Refresh Files
      </button>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                Filename
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                Uploaded
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white">
            {files.map((file) => (
              <tr key={file.id} className="border-b">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {file.filename}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(file.timestamp).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      file.status === "completed"
                        ? "bg-green-100 text-green-800"
                        : file.status === "processing"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {file.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() =>
                      handleDownloadOriginal(file.id, file.filename)
                    }
                    className="text-primary hover:text-blue-700 mr-4"
                  >
                    Download Original
                  </button>
                  <button
                    onClick={() => handleDownloadProcessed(file.id)}
                    className="text-primary hover:text-blue-700 mr-4"
                  >
                    Download Processed
                  </button>
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
