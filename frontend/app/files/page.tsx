"use client";

import { useState, useEffect } from "react";
import FileHistory from "../../components/FileHistory";
import { toast } from "react-hot-toast";

interface FileRecord {
  id: number;
  filename: string;
  count: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  timestamp: string;
}

export default function FilesPage() {
  const [fileRecords, setFileRecords] = useState<FileRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refreshFileHistory();
  }, []);

  const refreshFileHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("http://localhost:5005/api/files");
      const data = await response.json();

      // The API returns { files: [array] }, so we need to access the files array
      setFileRecords(data.files || []);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch file records");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteFile = async (fileId: number) => {
    if (
      !confirm(
        "Are you sure you want to delete this file? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/api/files/${fileId}/delete`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete file");
      }

      toast.success("File deleted successfully");
      refreshFileHistory();
    } catch (error) {
      toast.error("Failed to delete file");
    }
  };

  const handleDownloadResults = async (fileId: number) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/files/${fileId}/download`
      );

      if (!response.ok) {
        throw new Error("Failed to download results");
      }

      // Create a temporary link to trigger download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "results.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast.error("Failed to download results");
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">File Management</h1>

      <div className="mb-6">
        <button
          onClick={refreshFileHistory}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>

      <FileHistory
        fileRecords={fileRecords}
        isLoading={isLoading}
        error={error}
        onFileAction={(action, fileId) => {
          if (action === "delete") {
            handleDeleteFile(fileId);
          } else if (action === "download") {
            handleDownloadResults(fileId);
          }
        }}
        setResults={() => {}}
        setFileRecords={setFileRecords}
        setIsLoading={setIsLoading}
        setError={setError}
      />
    </div>
  );
}
