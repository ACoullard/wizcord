import { useServerList } from '@main/hooks/useServerList';
import ServerView from '@main/components/ServerView';

function MainScreen() {
  const { currentServer } = useServerList()

  return (
    <div className='flex flex-col h-screen'>
      <div className='bg-titlebar flex h-8 items-center justify-center text-white text-2xl p-2'>
        <p className='font-pixel'>Wizcord</p>
      </div>
      <div className='flex-1 flex'>
        <div className='bg-secondary w-16 flex flex-row items-start z-10'>
          <button className='ml-1'>
            <img className='w-13 h-12 rounded-full object-contain scale-100 mt-2' src="/Send-Image.jpg" alt="" />
          </button>
        </div>

        {currentServer && <ServerView serverId={currentServer.id} />}
      </div>
    </div>
  )
}

export default MainScreen
