import { useNavigate } from 'react-router-dom';
import { BACKEND_URL } from '@/constants';
import { useAuthStatusContext } from '@/contexts/AuthStatusContextProvider';

async function loginAnon(): Promise<boolean> {
  const endpoint = new URL("api/login/anonymous", BACKEND_URL)
  const responce = await fetch(endpoint, {
    method: 'POST',
    credentials: 'include', 
    headers: {
      'Content-Type': 'application/json'
    }
  })
  console.log(responce)
  return responce.ok
}



function LandingPage() {
  const navigate = useNavigate();
  const { setStateLoggedinAnonymous } = useAuthStatusContext();

  return (
  <div className="h-screen bg-lists flex flex-col justify-center items-center">
    <div className="flex flex-col items-center justify-center p-6 gap-4 rounded-2xl w-1/3 bg-secondary">
      <p className="font-pixel text-4xl text-white">
        Enter Wizcord!
      </p>
      <button
        className="w-4/5 h-14 bg-border text-white text-xl rounded-full font-pixel hover:bg-lists transition duration-300 ease-in-out"
        onClick={async () => {
          const success = await loginAnon();
          if (success) {
            setStateLoggedinAnonymous();
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
      className="px-5 py-1 bg-lists text-white rounded-full font-pixel border-2 border-secondary hover:bg-secondary transition duration-300 ease-in-out"
      onClick={() => { navigate("/login"); }}>
      Log In
    </button>
  </div>
  );
}

export default LandingPage;