import { useEffect, useState } from "react";
import { useVideo } from "../hooks/use-video";
import toast from "react-hot-toast";

export const CompressionStatus = () => {
  const { video } = useVideo();
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const videoId = video.name;

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL}/compression-status/${videoId}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prevMessages) => [...prevMessages, data.resolution]);
    };

    // Handle errors (optional, for debugging or fallback)
    eventSource.onerror = (error) => {
      toast.error("SSE error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="flex flex-col w-full gap-4 p-4 border rounded-xl">
      <h2>Compression Status</h2>
      {messages.length > 0 ? (
        messages.map((m, index) => (
          <div key={index} className="flex items-center space-x-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="24px"
              viewBox="0 -960 960 960"
              width="24px"
              fill="#75FB4C"
            >
              <path d="m424-296 282-282-56-56-226 226-114-114-56 56 170 170Zm56 216q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z" />
            </svg>
            <p>{m}</p>
          </div>
        ))
      ) : (
        <p>No updates yet.</p>
      )}
    </div>
  );
};
