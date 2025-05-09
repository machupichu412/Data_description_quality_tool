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
}

const FileUpload: React.FC<FileUploadProps> = ({
  setResults,
  setFileRecords,
  setIsLoading,
  setError,
  refreshFileHistory,
}) => {
  const [files, setFiles] = useState<File[]>([]);

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

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files[]", file);
    });

    try {
      const response = await axios.post(
        "http://localhost:5005/api/files/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Update file records with the new file information
      setFileRecords((prev) => [...prev, ...response.data.files]);
      setResults([]); // Clear results when new files are uploaded
      setFiles([]); // Clear the uploaded files list

      // Show success message
      toast.success("Files uploaded successfully");
    } catch (error) {
      console.error("Error uploading files:", error);
      setError("Failed to upload files. Please try again.");
      toast.error("Failed to upload files");
    } finally {
      setIsLoading(false);
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

      <button
        onClick={handleUpload}
        disabled={files.length === 0}
        className={`w-full py-2 px-4 rounded font-medium ${
          files.length === 0
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-primary text-white hover:bg-blue-700"
        }`}
      >
        Upload and Evaluate {files.length > 0 ? `(${files.length} files)` : ""}
      </button>
    </div>
  );
};

export default FileUpload;
