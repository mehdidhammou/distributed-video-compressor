import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { VideoProvider } from "./context/video";
import { Toaster } from "react-hot-toast";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <VideoProvider>
      <Toaster reverseOrder={false} />

      <App />
    </VideoProvider>
  </StrictMode>
);
