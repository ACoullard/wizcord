import './App.css'
import React from 'react';

function App() {
  return (
    <div className='flex flex-col min-h-screen'>
      {/* Top Title bar */}
      <div className='titlebar-bg flex h-7 items-center justify-center text-white text-2xl p-2'> <p className='font-Pixel'>Wizcord</p> </div>
      <div className='flex-1 flex'>
        {/* Div containing the server icons which refresh channels etc. */}
        <div className='secondary-bg w-16 flex flex-row items-start border-r-[#211C84] border-r-1'>
          <button className='ml-1'>
            <img className='w-13 h-12 rounded-full object-contain scale-100 mt-2' src="/Send-Image.jpg" alt=""/>
          </button>
        </div>
        {/* Channel List Div */}
        <div className='lists-bg w-1/7 flex flex-col'>
        <div className='secondary-bg text-center flex message-text h-1/25 p-1 mb-1 items-center justify-center border-b-2 border-color outline-l-[#4D55CC] outline-l-8'><p>Channel List</p></div>
        {/* A generic template for any channel, must include onclick react implementation onto top div */}
          <div className="flex flex-row h-1/30 px-2 items-center justify-center ">
            <div className='w-4 h-full flex items-center justify-center mr-1'><p>#</p></div>
            <div className='w-full h-full flex items-center'>Rules</div>
          </div>
          {/* Rounded divider between the servers */}
          <hr className="w-14/15 h-0.5 my-1 message-bg border-0 flex rounded-3xl mb-1.5 mx-auto"/>
          <div className="flex flex-row h-1/30 px-2 items-center justify-center">
            <div className='w-4 h-full flex items-center justify-center mr-1'><p>#</p></div>
            <div className='w-full h-full flex items-center'>General</div>
          </div>
        </div>
        {/* Message List Div, check if the same user sent the last message, if so, do not use their pfp */}
        <div className='message-bg w-29/42 flex flex-col p-2'>Messages Lists
          <div className='lists-bg text-white h-12 mt-auto rounded-full m-2 flex flex-row mb-3 shadow-md shadow-[#00FFFF]/70 focus-within:shadow-[0_0_20px_#00FFFF] transition delay-10 duration-400 ease-in-out'>
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

export default App
