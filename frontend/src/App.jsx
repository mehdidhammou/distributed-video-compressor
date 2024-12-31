import FIleUploadInput from "./components/file-upload-inpu";
import { useVideo } from "./hooks/use-video";
function App() {
  const { video } = useVideo();

  return (
    <div className="flex flex-col items-center justify-center w-full h-screen gap-8 p-2 pt-6 text-white bg-black md:gap-12 md:p-12">
      <div className="w-full">
        <h1 className="text-lg font-bold tracking-wide md:text-4xl">
          Distributed Video Compressor
        </h1>
        <span className="block mt-2 text-gray-500">
          Made by{""}
          <a
            href="https://github.com/mehdidhammou"
            className="ml-1 text-blue-200"
          >
            Mahdi Daddi Hammou
          </a>
        </span>
      </div>
      <div className="flex flex-col items-start justify-center w-full h-full gap-8 md:flex-row md:gap-12">
        <FIleUploadInput />
        <div className="w-full h-full overflow-hidden border border-gray-900 rounded-xl md:col-span-2">
          {video && (
            <video className="w-full h-full" controls>
              <source src={video} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
