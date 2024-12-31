import { useState } from "react";
import toast from "react-hot-toast";
import { useVideo } from "../hooks/use-video";

export default function FIleUploadInput() {
  const [isUploading, setIsUploading] = useState(false);
  const [file, setFile] = useState(null);

  const { setVideo } = useVideo();

  const handleFileChange = async (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      toast.error("Please select a file first.");
      return;
    }

    setVideo(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("video", file);
    try {
      setIsUploading(true);

      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const message = (await res.json()).message;
      toast.success(message);
    } catch (e) {
      console.log(e);
      toast.error(`Failed to upload the file. Please try again. ${e}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-full gap-2 md:max-w-fit md:gap-6">
      <label
        htmlFor="dropzone-file"
        className="flex flex-col items-center justify-center w-full h-64 p-8 border border-gray-900 cursor-pointer rounded-xl hover:bg-gray-100 dark:hover:border-gray-500 dark:hover:bg-gray-600"
      >
        <div className="flex flex-col items-center justify-center pt-5 pb-6">
          <svg
            className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 16"
          >
            <path
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
            />
          </svg>
          <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
            <span className="font-semibold">Click to upload</span> or drag and
            drop
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            SVG, PNG, JPG or GIF (MAX. 800x400px)
          </p>
        </div>
        <input
          id="dropzone-file"
          type="file"
          accept="video/*"
          className="hidden"
          onChange={handleFileChange}
        />
      </label>
      {file && (
        <p className="text-sm text-gray-500">Selected file: {file.name}</p>
      )}
      <button
        type="button"
        disabled={isUploading}
        onClick={handleFileUpload}
        className="text-white w-full bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
      >
        Upload
      </button>
    </div>
  );
}
