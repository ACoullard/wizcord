import { BACKEND_URL } from '@/constants';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

async function login(username: string, password: string): Promise<boolean> {
  const endpoint = new URL("api/login", BACKEND_URL)
  const responce = await fetch(endpoint, {
    method: 'POST',
    credentials: 'include', 
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  })
  console.log(responce)
  return responce.ok
}


function LogOn() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate();

  const SubmitValues = async (event: React.FormEvent) => {
    event.preventDefault()
    const success = await login(username, password)
    if (!success) {
        console.log("FAILED TO LOG IN")
    } else {
        console.log("Logged in!")
        navigate("/wizcord");
    }
  }
    return (
        <div className="h-screen bg-lists flex justify-center items-center">
            <div className="flex flex-col rounded-2xl h-1/3 w-1/3 bg-secondary py-8">
                <div className="h-1/8 flex items-center justify-center">
                    <p className="font-pixel text-4xl text-white">
                        Log Into Wizcord!
                    </p>
                </div>
                {/* <div className="bg-secondary w-full h-1 mt-5"></div> */}
                <div className="pt-4">
                    <form className="flex flex-col items-center" onSubmit={SubmitValues}>
                        <input
                            type="text"
                            placeholder="Username"
                            className="w-4/5 h-12 mb-4 rounded-full px-4 text-white bg-titlebar"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            className="w-4/5 h-12 mb-4 rounded-full px-4 text-white bg-titlebar"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
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