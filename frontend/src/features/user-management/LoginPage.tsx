function LogOn() {
    return (
        <div className="h-screen bg-lists flex justify-center items-center">
            <div className="flex flex-col rounded-2xl h-1/3 w-1/3 bg-secondary py-8">
                <div className="h-1/8 flex items-center justify-center">
                    <p className="font-pixel text-4xl text-white">
                        Log In Wizcord!
                    </p>
                </div>
                {/* <div className="bg-secondary w-full h-1 mt-5"></div> */}
                <div className="pt-4">
                    <form className="flex flex-col items-center">
                        <input
                            type="text"
                            placeholder="Username"
                            className="w-4/5 h-12 mb-4 rounded-full px-4 text-white bg-titlebar"
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            className="w-4/5 h-12 mb-4 rounded-full px-4 text-white bg-titlebar"
                        />
                        <button
                            type="submit"
                            className="w-4/5 h-12 bg-border text-white rounded-full font-pixel hover:bg-lists transition duration-300 ease-in-out">
                            Log In
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default LogOn;