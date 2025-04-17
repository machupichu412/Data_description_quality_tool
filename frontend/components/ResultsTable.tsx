import React, { useState } from 'react';
import axios from 'axios';

interface Result {
  description: string;
  decision: string;
  reasoning: string;
}

interface FileRecord {
  filename: string;
  id?: number;
  count?: number;
  pass_count?: number;
  fail_count?: number;
  pass_rate?: number;
  error?: string;
}

interface ResultsTableProps {
  results: Result[];
  fileRecords: FileRecord[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results, fileRecords }) => {
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  // Calculate statistics
  const totalCount = results.length;
  const passCount = results.filter(result => result.decision === 'PASS').length;
  const failCount = totalCount - passCount;
  const passPercentage = totalCount > 0 ? Math.round((passCount / totalCount) * 100) : 0;

  const handleDownload = async (fileId: number) => {
    if (!fileId) return;
    
    try {
      setDownloadingId(fileId);
      const response = await axios.get(`http://localhost:5005/api/download/${fileId}`, {
        responseType: 'blob'
      });
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `evaluation_results_${fileId}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading file:', error);
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div>
      {fileRecords.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Processed Files</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="py-2 px-3 text-left">File Name</th>
                  <th className="py-2 px-3 text-left">Descriptions</th>
                  <th className="py-2 px-3 text-left">Pass</th>
                  <th className="py-2 px-3 text-left">Fail</th>
                  <th className="py-2 px-3 text-left">Pass Rate</th>
                  <th className="py-2 px-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {fileRecords.map((record, idx) => (
                  <tr key={idx} className="border-t">
                    <td className="py-2 px-3 truncate max-w-xs">{record.filename}</td>
                    <td className="py-2 px-3">{record.count || 'N/A'}</td>
                    <td className="py-2 px-3 text-success">{record.pass_count || 'N/A'}</td>
                    <td className="py-2 px-3 text-danger">{record.fail_count || 'N/A'}</td>
                    <td className="py-2 px-3">
                      {record.pass_rate !== undefined ? `${Math.round(record.pass_rate)}%` : 'N/A'}
                    </td>
                    <td className="py-2 px-3">
                      {record.error ? (
                        <span className="text-danger text-sm">{record.error}</span>
                      ) : record.id ? (
                        <button
                          onClick={() => handleDownload(record.id!)}
                          disabled={downloadingId === record.id}
                          className="text-primary hover:text-blue-700 text-sm"
                        >
                          {downloadingId === record.id ? 'Downloading...' : 'Download CSV'}
                        </button>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-100 p-4 rounded shadow-sm">
          <h3 className="text-lg font-semibold">Total</h3>
          <p className="text-2xl">{totalCount}</p>
        </div>
        <div className="bg-green-100 p-4 rounded shadow-sm">
          <h3 className="text-lg font-semibold">Pass</h3>
          <p className="text-2xl text-success">{passCount}</p>
        </div>
        <div className="bg-red-100 p-4 rounded shadow-sm">
          <h3 className="text-lg font-semibold">Fail</h3>
          <p className="text-2xl text-danger">{failCount}</p>
        </div>
        <div className="bg-blue-100 p-4 rounded shadow-sm">
          <h3 className="text-lg font-semibold">Pass Rate</h3>
          <p className="text-2xl">{passPercentage}%</p>
        </div>
      </div>

      {results.length > 0 && (
        <div className="table-container">
          <h3 className="text-lg font-semibold mb-3">Evaluation Results</h3>
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="w-1/3">Description</th>
                <th className="w-1/6">Decision</th>
                <th className="w-1/2">Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index}>
                  <td className="whitespace-pre-wrap break-words">{result.description}</td>
                  <td className={result.decision === 'PASS' ? 'pass' : 'fail'}>
                    {result.decision}
                  </td>
                  <td className="whitespace-pre-wrap break-words">{result.reasoning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ResultsTable;
