import { useNavigate } from 'react-router-dom';
import { useAuthStatusContext } from '@/contexts/AuthStatusContextProvider';
import type { UserData } from '@main/types';

async function loginAnon(): Promise<{success: boolean, user: UserData | null}> {
  const response = await fetch("api/login/anonymous", {
    method: 'POST',
    credentials: 'include', 
    headers: {
      'Content-Type': 'application/json'
    }
  })
  console.log(response)
  const data = await response.json()
  const user = response.ok ? data as UserData : null
  return { success: response.ok, user: user }
}



function LandingPage() {
  const navigate = useNavigate();
  const { setStateLoggedinAnonymous } = useAuthStatusContext();

  return (
  <div className="h-screen bg-primary flex flex-col justify-center items-center">
    <div className="flex flex-col items-center justify-center p-6 gap-4 rounded-2xl w-1/3 bg-secondary">
      <p className="font-pixel text-4xl text-white">
        Enter Wizcord!
      </p>
      <button
        className="w-4/5 h-14 bg-highlight text-white text-xl rounded-full font-pixel hover:bg-primary transition duration-300 ease-in-out"
        onClick={async () => {
          const result = await loginAnon();
          if (result.success && result.user !== null) {
            setStateLoggedinAnonymous(result.user);
            navigate("/wizcord");
          } else {
            console.error("Login failed");
          }
        }}
      >
        Anonymous Login
      </button>
    </div>
    <p className="m-5 font-pixel text-xl text-white">Or</p>
    <button
      className="px-5 py-1 bg-primary text-white rounded-full font-pixel border-2 border-secondary hover:bg-secondary transition duration-300 ease-in-out"
      onClick={() => { navigate("/login"); }}>
      Log In
    </button>
  </div>
  );
}

export default LandingPage;