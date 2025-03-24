import React from 'react';

interface Result {
  description: string;
  decision: string;
  reasoning: string;
}

interface ResultsTableProps {
  results: Result[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  // Calculate statistics
  const totalCount = results.length;
  const passCount = results.filter(result => result.decision === 'PASS').length;
  const failCount = totalCount - passCount;
  const passPercentage = totalCount > 0 ? Math.round((passCount / totalCount) * 100) : 0;

  return (
    <div>
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

      <div className="table-container">
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
    </div>
  );
};

export default ResultsTable;
