// import './App.css'
import { useEffect } from 'react';
import ServerList from '@main/components/ServerList';
import MessageList from '@main/components/MessageList';
import { BACKEND_URL } from '@/constants';

let firstRun = true;

async function get_servers_data() {
  const endpoint = new URL("/servers", BACKEND_URL)
  try {
    const responce =  await fetch(endpoint)
    console.log(responce)
    if (!responce.ok) {
      throw new Error("unable to fetch servers data")
    }

    const json = await responce.json()
    console.log(json)
    return json
  } catch (error) {
    console.error(error);
  }
}

function MainScreen() {
  let serverData = {}
  useEffect(() => {
    if (firstRun) {
      get_servers_data().then((res)=>{
          serverData = res
        }
      )
      firstRun = false
    }
  }, [])
  
  console.log(serverData)
  return (
    <div className='flex flex-col min-h-screen'>
      {/* Top Title bar */}
      <div className='titlebar-bg flex h-8 items-center justify-center text-white text-2xl p-2'> <p className='font-Pixel'>Wizcord</p> </div>
      <div className='flex-1 flex'>
        {/* Div containing the server icons which refresh channels etc. */}
        <div className='secondary-bg w-16 flex flex-row items-start z-10'>
          <button className='ml-1'>
            <img className='w-13 h-12 rounded-full object-contain scale-100 mt-2' src="/Send-Image.jpg" alt=""/>
          </button>
        </div>
        {/* Channel List Div */}
        <div className='lists-bg w-1/7 flex flex-col p-b-0'>
          <div className='secondary-bg text-center flex message-text h-1/25 p-1 items-center justify-center border-b-1 border-b-[#211C84]'><p>Channel List</p></div>
        {/* A generic template for any channel, must include onclick react implementation onto top div */}
          <div className='p-2 h-full border-l-1 border-l-[#211C84] overflow-y-auto'>
            <ServerList />
          </div>
        </div>
        {/* Message List Div, check if the same user sent the last message, if so, do not use their pfp */}
        <div className='message-bg w-29/42 flex flex-col p-2'>
        {/* The Actual Messages listed through React function */}
          <div className='h-17/18 flex flex-col overflow-y-auto'>
            <MessageList />
          </div>
          <div className='lists-bg text-white h-1/18 mt-auto rounded-full m-2 flex flex-row mb-3 shadow-md shadow-[#00FFFF]/70 focus-within:shadow-[0_0_20px_#00FFFF] transition delay-10 duration-400 ease-in-out'>
            <input className ="shadow- appearance-none h-full rounded-full w-14/15 py-2 px-3 
            message-text leading-tight focus:outline-none focus:shadow-outline placeholder-white placeholder-Pixel" id="input" type="text" placeholder="Cast your spells here!"/>
            <button className='ml-2'>
              <img className='w-12 h-10 rounded-full object-contain scale-100' src="/Send-Image.jpg" alt=""/>
            </button>
          </div>
        </div>
        {/* Users List */}
        <div className='lists-bg w-1/6 flex p-2'>User List
        </div>
      </div>
    </div>
  )
}

export default MainScreen
