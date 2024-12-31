import { useContext } from "react";
import { VideoContext } from "../context/video";

export const useVideo = () => useContext(VideoContext);
