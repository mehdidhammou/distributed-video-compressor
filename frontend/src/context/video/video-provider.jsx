import { useState } from "react";
import { VideoContext } from "./video-context";

// eslint-disable-next-line react/prop-types
export const VideoProvider = ({ children }) => {
  const [video, setVideo] = useState(null);

  return (
    <VideoContext.Provider value={{ video, setVideo }}>
      {children}
    </VideoContext.Provider>
  );
};
