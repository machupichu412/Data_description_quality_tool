import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface FileUploadProps {
  setResults: React.Dispatch<React.SetStateAction<any[]>>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}

const FileUpload: React.FC<FileUploadProps> = ({ setResults, setIsLoading, setError }) => {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please upload a valid CSV file');
    }
  }, [setError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5005/api/evaluate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResults(response.data.results);
    } catch (error) {
      console.error('Error uploading file:', error);
      if (axios.isAxiosError(error) && error.response) {
        setError(`Error: ${error.response.data.error || 'Failed to process file'}`);
      } else {
        setError('Error connecting to server. Please make sure the backend is running.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the CSV file here...</p>
        ) : (
          <div>
            <p className="mb-2">Drag & drop a CSV file here, or click to select a file</p>
            <p className="text-sm text-gray-500">Only CSV files with a 'description' column are accepted</p>
          </div>
        )}
      </div>

      {file && (
        <div className="flex items-center justify-between bg-gray-100 p-3 rounded">
          <span className="truncate max-w-xs">{file.name}</span>
          <span className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file}
        className={`w-full py-2 px-4 rounded font-medium ${
          !file
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-primary text-white hover:bg-blue-700'
        }`}
      >
        Upload and Evaluate
      </button>
    </div>
  );
};

export default FileUpload;
