import FIleUploadInput from "./components/file-upload-inpu";

function App() {
  return (
    <>
      <div className="flex flex-col items-center justify-center w-full h-screen gap-12 p-12 text-white bg-black">
        <h1 className="w-full text-4xl font-bold tracking-wide">
          Distributed Video Compressor
        </h1>
        <div className="grid items-center justify-center w-full h-full gap-12 md:grid-cols-3">
          <div className="flex flex-col items-center justify-start h-full gap-12 border md:col-span-1">
            <FIleUploadInput />
            <div className="w-full h-full border">worker status here</div>
          </div>
          <div className="w-full h-full border md:col-span-2">
            video showcase here
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
