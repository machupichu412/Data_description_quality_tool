import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { toast } from "react-toastify";

interface FileUploadProps {
  setResults: React.Dispatch<React.SetStateAction<any[]>>;
  setFileRecords: React.Dispatch<React.SetStateAction<any[]>>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  refreshFileHistory: () => void;
  isLoading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  setResults,
  setFileRecords,
  setIsLoading,
  setError,
  refreshFileHistory,
  isLoading,
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState<number>(0);
  const [currentFile, setCurrentFile] = useState<string>("");

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const validFiles = acceptedFiles.filter((file) =>
        file.name.endsWith(".csv")
      );
      if (validFiles.length > 0) {
        setFiles((prev) => [...prev, ...validFiles]);
        setError(null);
      } else if (acceptedFiles.length > 0) {
        setError("Please upload valid CSV files only");
      }
    },
    [setError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError("Please select at least one file to upload");
      return;
    }

    setIsLoading(true);
    setError(null);
    setProgress(0);
    setCurrentFile("");

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files[]", file);
    });

    try {
      const response = await axios.post(
        "http://localhost:5005/api/evaluate",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          },
        }
      );

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      // Update file records with the new file information
      setFileRecords((prev) => [...prev, ...response.data.files]);
      setResults(response.data.results); // Set the results directly
      setFiles([]); // Clear the uploaded files list

      // Show success message
      toast.success("Files evaluated successfully");
    } catch (error) {
      console.error("Error evaluating files:", error);
      setError(
        error instanceof Error
          ? error.message
          : "Failed to evaluate files. Please try again."
      );
      toast.error("Failed to evaluate files");
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="space-y-4">
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the CSV files here...</p>
        ) : (
          <div>
            <p className="mb-2">
              Drag & drop CSV files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Only CSV files with a 'description' column are accepted
            </p>
            <p className="text-sm text-gray-500 mt-1">
              You can upload multiple files at once
            </p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          <h3 className="font-medium">Selected Files ({files.length})</h3>
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-gray-100 p-3 rounded"
            >
              <span className="truncate max-w-xs">{file.name}</span>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </span>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="text-sm text-gray-500">{progress}%</span>
          </div>
          {currentFile && (
            <p className="mt-2 text-sm text-gray-500">
              Currently processing: {currentFile}
            </p>
          )}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={files.length === 0}
        className={`w-full py-2 px-4 rounded font-medium ${
          files.length === 0
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-primary text-white hover:bg-blue-700"
        }`}
      >
        Evaluate {files.length > 0 ? `(${files.length} files)` : ""}
      </button>
    </div>
  );
};

export default FileUpload;
