import { useState } from 'react'
import './App.css'

function serverList() {
  return (<a href='https://www.google.com' target="_blank"> </a>)
}

function App() {
  const servers = serverList();
  return (
      <div className='flex flex-col min-h-screen'>
        <div className='bg-[#096B68] flex h-7 items-center justify-center text-white text-2xl p-2'> <p className='font-Pixel'>Wizcord</p> </div>
        <div className='flex-1 bg-blue-400 flex'>
          <div className='bg-[#129990] w-16 flex flex-row items-start'>
            <button className='ml-1'>
                <img className='w-13 h-12 rounded-full object-contain scale-100 mt-2' src="/Send-Image.jpg" alt="" />
            </button>
          </div>
          <div className='bg-[#90D1CA] w-1/7 flex flex-col p-2'>Channel List
            <div class="w-1/3"><h1>hello</h1></div>
            <div class><h1>hi</h1></div>
          </div>
          <div className='bg-[#FFFBDE] w-29/42 flex flex-col p-2'>Messages Lists
            <div className='bg-[#90D1CA] text-white h-12 mt-auto rounded-full m-2 flex flex-row mb-3 shadow-md shadow-[#00FFFF]/70 focus-within:shadow-[0_0_20px_#00FFFF] 
            transition delay-10 duration-400 ease-in-out'>
              <input className ="shadow- appearance-none h-full rounded-full w-14/15 py-2 px-3 
              text-[#FFFBDE] leading-tight focus:outline-none focus:shadow-outline placeholder-white placeholder-Pixel" id="input" type="text" placeholder="Cast your spells here!"/>
              <button className='ml-2'>
                <img className='w-12 h-10 rounded-full object-contain scale-100' src="/Send-Image.jpg" alt=""/>
              </button>
            </div>
          </div>
          <div className='bg-[#90D1CA] w-1/6 flex p-2'>User List
            {servers}
          </div>
        </div>
      </div>
  )
}

export default App
