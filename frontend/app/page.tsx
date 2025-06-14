"use client";

<<<<<<< HEAD
import { useState, useRef } from "react";
import FileUpload from "../components/FileUpload";
import ResultsTable from "../components/ResultsTable";
import FileHistory from "../components/FileHistory";
import ProcessingQueue from "../components/ProcessingQueue";
=======
import { useState } from "react";
import FileUpload from "../components/FileUpload";
import ResultsTable from "../components/ResultsTable";
import FileHistory from "../components/FileHistory";
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)

interface Result {
  description: string;
  decision: string;
  reasoning: string;
}

interface FileRecord {
  id: number;
  filename: string;
  count: number;
  pass_count: number;
  fail_count: number;
  pass_rate: number;
  timestamp: string;
}

export default function Home() {
  const [results, setResults] = useState<Result[] | null>(null);
  const [fileRecords, setFileRecords] = useState<FileRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const refreshFileHistory = () => {
    // This function will be passed to child components to trigger file history refresh
    const fileHistoryComponent = document.getElementById(
      "file-history-component"
    );
    if (fileHistoryComponent) {
      const refreshButton = fileHistoryComponent.querySelector("button");
      if (refreshButton) refreshButton.click();
    }
    // Also refresh the processing queue
    setRefreshTrigger((prev) => prev + 1);
  };

  // Initialize results as empty array if undefined
  const safeResults = results || [];

  return (
    <div className="flex flex-col gap-8">
      <div id="file-history-component">
        <FileHistory
<<<<<<< HEAD
          fileRecords={fileRecords}
          isLoading={isLoading}
          error={error}
=======
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
          setResults={setResults}
          setFileRecords={setFileRecords}
          setIsLoading={setIsLoading}
          setError={setError}
        />
      </div>

      <ProcessingQueue refreshTrigger={refreshTrigger} />

      <section className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">
          Data Description Quality Evaluator
        </h2>
        <p className="mb-4">
          Upload CSV files containing data descriptions to evaluate their
          quality. Files must include a column named &quot;description&quot;.
        </p>
        <FileUpload
          setResults={setResults}
          setFileRecords={setFileRecords}
          setIsLoading={setIsLoading}
          setError={setError}
          refreshFileHistory={refreshFileHistory}
        />
      </section>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      )}

<<<<<<< HEAD
      {safeResults.length > 0 && !isLoading && (
=======
      {results && results.length > 0 && !isLoading && (
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
        <section className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Evaluation Results</h2>
          <ResultsTable results={safeResults} fileRecords={fileRecords} />
        </section>
      )}
    </div>
  );
}
