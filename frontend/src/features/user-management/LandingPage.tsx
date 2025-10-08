


function LandingPage() {
  
  return (
  <div className="h-screen bg-lists flex flex-col justify-center items-center">
    <div className="flex flex-col items-center justify-center p-6 gap-4 rounded-2xl w-1/3 bg-secondary">
      <p className="font-pixel text-4xl text-white">
        Enter Wizcord!
      </p>
      <button
        className="w-4/5 h-12 bg-border text-white rounded-full font-pixel hover:bg-lists transition duration-300 ease-in-out">
        Anonymous Login
      </button>
      {/* <div className="h-1/8 flex-col items-center justify-center m-5">
        <p className="font-pixel text-4xl text-white">
          Enter Wizcord!
        </p>
      </div>
      <div className="py-4 flex flex-col items-center">
        <button
          className="w-4/5 h-12 bg-border text-white rounded-full font-pixel hover:bg-lists transition duration-300 ease-in-out">
          Anonymous Login
        </button>
      </div> */}
    </div>
    <p className="m-5 font-pixel text-xl text-white">Or</p>
    <button
      className="px-5 py-1 bg-border text-white rounded-full font-pixel hover:bg-lists border-2 border-secondary transition duration-300 ease-in-out">
      Log In
    </button>
  </div>
  );
}

export default LandingPage;