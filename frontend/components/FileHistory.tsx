import React, { useState, useEffect } from "react";
import axios from "axios";

interface FileRecord {
  id: number;
  filename: string;
  count: number;
  pass_count: number;
  fail_count: number;
  pass_rate?: number;
  timestamp: string;
  status?: string;
}

interface FileHistoryProps {
  fileRecords: FileRecord[];
  isLoading?: boolean;
  error?: string | null;
  onFileAction?: (action: "delete" | "download", fileId: number) => void;
  setResults: React.Dispatch<React.SetStateAction<any[]>>;
  setFileRecords: React.Dispatch<React.SetStateAction<any[]>>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}

const FileHistory: React.FC<FileHistoryProps> = ({
  fileRecords,
  isLoading = false,
  error = null,
  onFileAction,
  setResults,
  setFileRecords,
  setIsLoading,
  setError,
}) => {
  const [loadingFileId, setLoadingFileId] = useState<number | null>(null);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatPassRate = (rate: number | undefined) => {
    if (rate === undefined) {
      return "-";
    }
    return `${rate.toFixed(1)}%`;
  };

  const handleViewResults = async (fileId: number) => {
    setLoadingFileId(fileId);
    setIsLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:5005/api/files/descriptions/${fileId}`
      );
      const fileData = {
        id: fileId,
        filename: response.data.file?.fname || "Unknown",
        count: response.data.descriptions?.length || 0,
        pass_count:
          response.data.descriptions?.filter((r: any) => r.decision === "PASS")
            .length || 0,
        fail_count:
          response.data.descriptions?.filter((r: any) => r.decision === "FAIL")
            .length || 0,
        pass_rate:
          response.data.descriptions?.length > 0
            ? (response.data.descriptions.filter(
                (r: any) => r.decision === "PASS"
              ).length /
                response.data.descriptions.length) *
              100
            : 0,
      };

      // Update results and keep existing file records
      setResults(response.data.descriptions || []);
      setFileRecords((prevRecords) =>
        prevRecords.map((record) =>
          record.id === fileId ? { ...record, ...fileData } : record
        )
      );
    } catch (error) {
      console.error("Error fetching file results:", error);
      setError("Failed to load results for this file");
    } finally {
      setLoadingFileId(null);
      setIsLoading(false);
    }
  };

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <h2 className="text-xl font-semibold mb-4">File History</h2>
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">{error}</div>
      )}
      <table className="w-full">
        <thead>
          <tr>
            <th className="text-left py-3 px-4">Filename</th>
            <th className="text-left py-3 px-4">Date</th>
            <th className="text-left py-3 px-4">Total</th>
            <th className="text-left py-3 px-4">Pass</th>
            <th className="text-left py-3 px-4">Fail</th>
            <th className="text-left py-3 px-4">Pass Rate</th>
            <th className="text-left py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={7} className="text-center py-4">
                Loading...
              </td>
            </tr>
          ) : fileRecords.length === 0 ? (
            <tr>
              <td colSpan={7} className="text-center py-4">
                No files uploaded yet
              </td>
            </tr>
          ) : (
            fileRecords.map((file) => (
              <tr key={file.id} className="border-b">
                <td className="py-3 px-4">{file.filename}</td>
                <td className="py-3 px-4">{formatDate(file.timestamp)}</td>
                <td className="py-3 px-4">{file.count}</td>
                <td className="py-3 px-4">{file.pass_count}</td>
                <td className="py-3 px-4">{file.fail_count}</td>
                <td className="py-3 px-4">{formatPassRate(file.pass_rate)}</td>
                <td className="py-3 px-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleViewResults(file.id)}
                      disabled={loadingFileId === file.id}
                      className="px-2 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                    >
                      {loadingFileId === file.id
                        ? "Loading..."
                        : "View Results"}
                    </button>
                    {onFileAction && (
                      <>
                        <button
                          onClick={() => onFileAction("download", file.id)}
                          className="px-2 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                        >
                          Download
                        </button>
                        <button
                          onClick={() => onFileAction("delete", file.id)}
                          className="px-2 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FileHistory;
