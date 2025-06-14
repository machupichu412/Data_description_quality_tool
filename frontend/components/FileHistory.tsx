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
<<<<<<< HEAD
  fileRecords,
  isLoading = false,
  error = null,
  onFileAction,
=======
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
  setResults,
  setFileRecords,
  setIsLoading,
  setError,
}) => {
  const [loadingFileId, setLoadingFileId] = useState<number | null>(null);

<<<<<<< HEAD
=======
  const fetchFileHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await axios.get("http://localhost:5005/api/files");
      setHistory(response.data.files || []);
    } catch (error) {
      console.error("Error fetching file history:", error);
      setError("Failed to fetch file history");
    } finally {
      setLoadingHistory(false);
    }
  };

>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
  useEffect(() => {
    // Fetch initial file records if none exist
    if (fileRecords.length === 0 && !isLoading) {
      fetchFileRecords();
    }
  }, [fileRecords, isLoading]);

  const fetchFileRecords = async () => {
    try {
<<<<<<< HEAD
      setIsLoading(true);
      const response = await axios.get("http://localhost:5005/api/files");
      setFileRecords(response.data.files || []);
    } catch (error) {
      console.error("Error fetching file records:", error);
      setError("Failed to load file history");
=======
      const response = await axios.get(
        `http://localhost:5005/api/files/${fileId}/descriptions`
      );
      const { file, descriptions } = response.data;

      // Set results and calculate statistics
      if (!descriptions) {
        throw new Error("No descriptions found for this file");
      }

      setResults(descriptions);

      // Calculate statistics
      const passCount = descriptions.filter(
        (d: any) => d.decision === "PASS"
      ).length;
      const failCount = descriptions.length - passCount;
      const passRate =
        descriptions.length > 0 ? (passCount / descriptions.length) * 100 : 0;

      setFileRecords([
        {
          id: fileId,
          filename: file?.filename || "Unknown",
          count: descriptions.length,
          pass_count: passCount,
          fail_count: failCount,
          pass_rate: passRate,
        },
      ]);
    } catch (error) {
      console.error("Error fetching file results:", error);
      setError("Failed to load results for this file");
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
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
<<<<<<< HEAD
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
=======
    <div className="bg-gray-50 p-6 rounded-lg shadow-sm mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Recent Files</h3>
        <button
          onClick={fetchFileHistory}
          className="text-primary hover:text-blue-700 text-sm"
          disabled={loadingHistory}
        >
          {loadingHistory ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {loadingHistory ? (
        <p className="text-gray-500">Loading file history...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-3 text-left">File Name</th>
                <th className="py-2 px-3 text-left">Descriptions</th>
                <th className="py-2 px-3 text-left">Pass Rate</th>
                <th className="py-2 px-3 text-left">Uploaded</th>
                <th className="py-2 px-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {history.map((file) => (
                <tr key={file.id} className="border-t hover:bg-gray-50">
                  <td className="py-2 px-3 truncate max-w-xs">
                    {file.filename}
                  </td>
                  <td className="py-2 px-3">{file.count}</td>
                  <td className="py-2 px-3">
                    <span
                      className={
                        file.pass_rate >= 70 ? "text-success" : "text-danger"
                      }
                    >
                      {Math.round(file.pass_rate)}%
                    </span>
                  </td>
                  <td className="py-2 px-3 text-sm text-gray-600">
                    {formatDate(file.timestamp)}
                  </td>
                  <td className="py-2 px-3">
                    <button
                      onClick={() => handleViewResults(file.id)}
                      disabled={loadingFileId === file.id}
                      className="text-primary hover:text-blue-700 text-sm mr-3"
                    >
                      {loadingFileId === file.id
                        ? "Loading..."
                        : "View Results"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
        </div>
      )}
    </div>
  );
};

export default FileHistory;
