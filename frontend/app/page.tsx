'use client'

import { useState } from 'react'
import FileUpload from '../components/FileUpload'
import ResultsTable from '../components/ResultsTable'

interface Result {
  description: string;
  decision: string;
  reasoning: string;
}

export default function Home() {
  const [results, setResults] = useState<Result[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="flex flex-col gap-8">
      <section className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Data Description Quality Evaluator</h2>
        <p className="mb-4">
          Upload a CSV file containing data descriptions to evaluate their quality. 
          The file must include a column named &quot;description&quot;.
        </p>
        <FileUpload 
          setResults={setResults} 
          setIsLoading={setIsLoading} 
          setError={setError} 
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

      {results.length > 0 && !isLoading && (
        <section className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Evaluation Results</h2>
          <ResultsTable results={results} />
        </section>
      )}
    </div>
  )
}
