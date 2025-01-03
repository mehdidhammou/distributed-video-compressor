import { CompressionStatus } from "./components/compression-status";
import FileUploadInput from "./components/file-upload-input";
import { useVideo } from "./hooks/use-video";
function App() {
  const { video } = useVideo();

  return (
    <div className="text-white bg-black">
      <div className="flex flex-col items-center justify-center w-full h-screen gap-8 p-2 pt-6 mx-auto max-w-[100rem] md:p-12 md:gap-12">
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
          <div className="flex flex-col items-center justify-center w-full gap-2 md:max-w-fit md:gap-6">
            <FileUploadInput />
            {video && <CompressionStatus />}
          </div>
          <div className="w-full h-full overflow-hidden border border-gray-900 aspect-auto rounded-xl md:col-span-2">
            {video && (
              <video className="w-full h-full aspect-video" controls>
                <source src={URL.createObjectURL(video)} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
