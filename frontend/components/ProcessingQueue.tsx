import React, { useState, useEffect } from "react";
import axios from "axios";

interface QueueItem {
  id: number;
  file_name: string;
  status: "waiting" | "processing" | "completed" | "error";
  progress?: number;
  upload_date: string;
  error?: string;
}

interface ProcessingQueueProps {
  refreshTrigger: number;
}

const ProcessingQueue: React.FC<ProcessingQueueProps> = ({
  refreshTrigger,
}) => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(
    null
  );

  // Check if there are any active items that need polling
  const hasActiveItems = (items: QueueItem[]) => {
    return items.some(
      (item) => item.status === "waiting" || item.status === "processing"
    );
  };

  // Check if we should show the queue component
  const shouldShowQueue = (items: QueueItem[]) => {
    return (
      hasActiveItems(items) ||
      items.some(
        (item) => item.status === "completed" || item.status === "error"
      )
    );
  };

  // Fetch queue status
  const fetchQueueStatus = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://localhost:5005/api/queue");

      // Map the queue items to our component's format
      const queueData = response.data.queue.map((item: any) => ({
        id: item.id,
        file_name: item.file_name,
        status: item.status,
        progress: item.progress,
        upload_date: item.upload_date,
        error: item.error,
      }));

      setQueueItems(queueData);

      // Only continue polling if there are active items
      if (pollingInterval && !hasActiveItems(queueData)) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    } catch (error) {
      console.error("Error fetching queue status:", error);
    } finally {
      setLoading(false);
    }
  };

  // Add a debounce function
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return function executedFunction(...args: any[]) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  // Debounced fetch function
  const debouncedFetchQueueStatus = debounce(fetchQueueStatus, 1000);

  // Fetch queue status on component mount and when refreshTrigger changes
  useEffect(() => {
    // Initial fetch
    debouncedFetchQueueStatus();

    // Start polling if there are active items
    if (hasActiveItems(queueItems)) {
      // Increased polling interval to 10 seconds
      const intervalId = setInterval(debouncedFetchQueueStatus, 10000);
      setPollingInterval(intervalId);
    }

    // Cleanup interval on unmount
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [refreshTrigger, queueItems]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Only render the queue component when there are items to show
  if (!shouldShowQueue(queueItems)) {
    return null;
  }

  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-sm mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Processing Queue</h3>
        <button
          onClick={debouncedFetchQueueStatus}
          className="text-primary hover:text-blue-700 text-sm"
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {loading && queueItems.length === 0 ? (
        <p className="text-gray-500">Loading queue information...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-3 text-left">File Name</th>
                <th className="py-2 px-3 text-left">Uploaded</th>
                <th className="py-2 px-3 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {queueItems.map((item) => (
                <tr
                  key={item.id}
                  className={`border-t ${
                    item.status === "processing"
                      ? "bg-blue-50"
                      : "hover:bg-gray-50"
                  }`}
                >
                  <td className="py-2 px-3 truncate max-w-xs">
                    {item.file_name}
                  </td>
                  <td className="py-2 px-3 text-sm text-gray-600">
                    {formatDate(item.upload_date)}
                  </td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        item.status === "waiting"
                          ? "bg-yellow-100 text-yellow-800"
                          : item.status === "processing"
                          ? "bg-blue-100 text-blue-800"
                          : item.status === "completed"
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {item.status}
                    </span>
                    {item.progress !== undefined && (
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full"
                          style={{ width: `${item.progress}%` }}
                        ></div>
                      </div>
                    )}
                    {item.error && (
                      <span className="text-red-500">{item.error}</span>
                    )}
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

export default ProcessingQueue;
