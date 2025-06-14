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

  useEffect(() => {
    // Fetch initial file records if none exist
    if (fileRecords.length === 0 && !isLoading) {
      fetchFileRecords();
    }
  }, [fileRecords, isLoading]);

  const fetchFileRecords = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get("http://localhost:5005/api/files");
      setFileRecords(response.data.files || []);
    } catch (error) {
      console.error("Error fetching file records:", error);
      setError("Failed to load file history");
    } finally {
      setIsLoading(false);
    }
  };

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

  const handleDownloadResults = async (fileId: number) => {
    // Implement download logic here
  };

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">File History</h2>

      {isLoading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      )}

      {fileRecords.length === 0 && !isLoading && (
        <p className="text-gray-500">No files have been evaluated yet</p>
      )}

      {fileRecords.length > 0 && (
        <div className="space-y-4">
          {fileRecords.map((record) => (
            <div
              key={record.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-4">
                <div className="flex flex-col">
                  <span className="font-medium">{record.filename}</span>
                  <span className="text-sm text-gray-500">
                    {formatDate(record.timestamp)}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex flex-col items-end">
                  <span className="text-sm text-gray-500">Total:</span>
                  <span className="font-medium">{record.count}</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-sm text-gray-500">Pass:</span>
                  <span className="font-medium text-green-500">
                    {record.pass_count}
                  </span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-sm text-gray-500">Fail:</span>
                  <span className="font-medium text-red-500">
                    {record.fail_count}
                  </span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-sm text-gray-500">Pass Rate:</span>
                  <span className="font-medium">
                    {formatPassRate(record.pass_rate)}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleViewResults(record.id)}
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-blue-700"
                  disabled={loadingFileId === record.id}
                >
                  View Results
                </button>
                <button
                  onClick={() => handleDownloadResults(record.id)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                >
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileHistory;
