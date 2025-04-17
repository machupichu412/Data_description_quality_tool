import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface FileRecord {
  id: number;
  filename: string;
  count: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  timestamp: string;
}

interface FileHistoryProps {
  setResults: React.Dispatch<React.SetStateAction<any[]>>;
  setFileRecords: React.Dispatch<React.SetStateAction<any[]>>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}

const FileHistory: React.FC<FileHistoryProps> = ({ 
  setResults, 
  setFileRecords, 
  setIsLoading, 
  setError 
}) => {
  const [history, setHistory] = useState<FileRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingFileId, setLoadingFileId] = useState<number | null>(null);

  const fetchFileHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await axios.get('http://localhost:5005/api/files');
      setHistory(response.data.files || []);
    } catch (error) {
      console.error('Error fetching file history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchFileHistory();
  }, []);

  const handleViewResults = async (fileId: number) => {
    setLoadingFileId(fileId);
    setIsLoading(true);
    try {
      const response = await axios.get(`http://localhost:5005/api/descriptions/${fileId}`);
      setResults(response.data.results || []);
      setFileRecords([{
        id: fileId,
        filename: history.find(file => file.id === fileId)?.filename || 'Unknown',
        count: response.data.results?.length || 0,
        pass_count: response.data.results?.filter((r: any) => r.decision === 'PASS').length || 0,
        fail_count: response.data.results?.filter((r: any) => r.decision === 'FAIL').length || 0,
        pass_rate: response.data.results?.length > 0 
          ? (response.data.results.filter((r: any) => r.decision === 'PASS').length / response.data.results.length) * 100 
          : 0
      }]);
    } catch (error) {
      console.error('Error fetching file results:', error);
      setError('Failed to load results for this file');
    } finally {
      setLoadingFileId(null);
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (history.length === 0 && !loadingHistory) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg shadow-sm mb-6">
        <h3 className="text-lg font-semibold mb-2">Recent Files</h3>
        <p className="text-gray-500">No files have been uploaded yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-sm mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Recent Files</h3>
        <button 
          onClick={fetchFileHistory}
          className="text-primary hover:text-blue-700 text-sm"
          disabled={loadingHistory}
        >
          {loadingHistory ? 'Refreshing...' : 'Refresh'}
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
                  <td className="py-2 px-3 truncate max-w-xs">{file.file_name}</td>
                  <td className="py-2 px-3">{file.description_count}</td>
                  <td className="py-2 px-3">
                    <span className={file.pass_rate >= 70 ? 'text-success' : 'text-danger'}>
                      {Math.round(file.pass_rate)}%
                    </span>
                  </td>
                  <td className="py-2 px-3 text-sm text-gray-600">{formatDate(file.timestamp)}</td>
                  <td className="py-2 px-3">
                    <button
                      onClick={() => handleViewResults(file.id)}
                      disabled={loadingFileId === file.id}
                      className="text-primary hover:text-blue-700 text-sm mr-3"
                    >
                      {loadingFileId === file.id ? 'Loading...' : 'View Results'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default FileHistory;
