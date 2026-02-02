import { useEffect, useState, useRef, useLayoutEffect } from 'react';
import ChannelList from '@/features/main/components/ChannelList';
import MessageList from '@main/components/MessageList';
import { useServerDataCache } from '@main/hooks/useServerDataCache';
import { useMessageSSEListener } from '@main/hooks/useSSEListener';
import { useServerList } from '@main/hooks/useServerList';
import { useAuthStatusContext } from '@/contexts/AuthStatusContextProvider';
import type { MessageData, ServerData, ChannelData, ServerMemberData } from '@main/types';
import TextareaAutosize from 'react-textarea-autosize';

async function getMessages(channelId: string): Promise<MessageData[]> {
  const endpoint = new URL(`api/channel/${channelId}`, window.location.origin);
  endpoint.searchParams.set("limit", "100")
  const responce = await fetch(endpoint, {
    credentials: 'include'
  })
  if (!responce.ok) {
      throw new Error("unable to fetch message data")
    }
  const json = await responce.json()
  const messagesList: MessageData[] = json["data"].map((message:any) => ({
    id: message.id,
    content: message.content,
    timestamp: new Date(message.timestamp),
    user: message.author_id
  }))
  console.log("messageList: ")
  console.log(messagesList)
  return messagesList
}

async function postMessage(message: string, channel_id: string) {
  // console.log(message)
  const endpoint = `api/channel/${channel_id}/post`
  const responce = await fetch(endpoint, {
    method: 'POST',
    credentials: 'include', 
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: message
    })
  })
  return responce.ok
}

function MainScreen() {
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { serverList, currentServer, setCurrentServer } = useServerList()
  const get_server_data = useServerDataCache()

  const { userData } = useAuthStatusContext()

  const [channelsList, setChannelsList] = useState<ChannelData[]>([])
  const [currentChannel, setCurrentChannel] = useState<ChannelData>()

  const [userList, setUserList] = useState<ServerMemberData[]>([])

  const [messagesList, setMessagesList] = useState<MessageData[]>([])
  const messageScrollContainer = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    if (currentServer == undefined) {
      return
    }
    console.log("Fetching server data for:", currentServer.id)
    get_server_data(currentServer.id)
    .then((server_data) => {
      setChannelsList(server_data.channels)
      setCurrentChannel(server_data.channels[0])

      setUserList(server_data.users)
    }).catch((error) => {
      console.error(error)
    })
  }, [currentServer, get_server_data])
  
  
  useEffect(() => {
    if (currentChannel == undefined) {
      return
    }
    console.log("ran this")
    getMessages(currentChannel.id).then((data) => {
      setMessagesList([...data])
    })
  }, [currentChannel])
  
  useLayoutEffect(() => {
    if (messageScrollContainer.current) {
        messageScrollContainer.current.scrollTop = messageScrollContainer.current.scrollHeight;
    }
  }, [messagesList])
  
  
  function handleMessageSubmit(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey && inputRef.current != null && currentChannel) {
      event.preventDefault()
      const text = inputRef.current.value.trim()
      if (!text) return
      postMessage(text, currentChannel.id)
        .then((succeeded) => {
          if (succeeded && inputRef.current != null) inputRef.current.value = ""
          else console.error("message failed to send")
        })
    }
  }
  
  function incomingMessageHandler(data: MessageData) {
    console.log("incoming message:", data.content)
    setMessagesList(prevMessages => [...prevMessages, data])
  }
  
  useMessageSSEListener(currentChannel?.id, incomingMessageHandler)
  
  return (
    <div className='flex flex-col h-screen'>
      {/* Top Title bar */}
      <div className='bg-titlebar flex h-8 items-center justify-center text-white text-2xl p-2'> <p className='font-pixel'>Wizcord</p> </div>
      <div className='flex-1 flex'>
        {/* Div containing the server icons which refresh channels etc. */}
        <div className='bg-secondary w-16 flex flex-row items-start z-10'>
          <button className='ml-1'>
            <img className='w-13 h-12 rounded-full object-contain scale-100 mt-2' src="/Send-Image.jpg" alt=""/>
          </button>
        </div>
        {/* Channel List Div */}
        <div className='bg-primary border-l-3 border-l-[#5a61cc] w-1/7 flex flex-col p-b-0'>
          <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'><p>Channel List</p></div>
          {/* A generic template for any channel, must include onclick react implementation onto top div */}
          <div className='p-2 bg-secondary h-full overflow-y-auto'>
            <ChannelList onChannelClick={(name) => {
              const channeldata = channelsList.find(channel => channel.name == name)
              setCurrentChannel(channeldata)}}
            channelNames={channelsList.map(item => item["name"])}/>
          </div>
        </div>
        {/* Message List Div, check if the same user sent the last message, if so, do not use their pfp */}
        <div className='bg-primary w-29/42 flex flex-col p-2'>
        {/* The Actual Messages listed through React function */}
          <div className='flex-grow relative'>
            <div ref={messageScrollContainer} className='overflow-y-auto h-full w-full absolute'>
              <MessageList 
                messages={messagesList}
                users={userList}/>
            </div>
          </div>
          {/* TODO: This should probably be broken out into another component at this point*/}
          <div className='bg-tertiary min-h-1/18 mt-auto rounded-4xl m-2 flex flex-row items-center
            shadow-[0_0_16px_rgba(0,255,255,0.5)] 
            hover:shadow-[0_0_18px_rgba(0,255,255,0.7)] 
            focus-within:shadow-[0_0_20px_#00FFFF]
            hover:focus-within:shadow-[0_0_23px_#00FFFF] 
            transition duration-400 ease-in-out'>
            <TextareaAutosize
              ref={inputRef}
              className ="flex-grow py-2 px-5 break-all resize-none
              message-text leading-tight focus:outline-none focus:shadow-outline placeholder-pixel" 
              id="input"
              placeholder="Cast your spells here!"
              autoCorrect='off'
              autoComplete='off'
              data-lpignore='true'
              onKeyDown={handleMessageSubmit}
            />
            <button className='flex w-12 aspect-square p-1'>
              <img className='rounded-full h-full w-full object-contain' src="/Send-Image.jpg" alt=""/>
            </button>
          </div>
        </div>
        {/* Users List */}
        <div className='bg-secondary w-1/6 flex flex-col'>
          <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'><p>Current User</p></div>
              <p className='px-4'>{userData?.username}</p>
          <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'><p>User List</p></div>
          <div className='p-4'>
            {userList.map(user => <p>{user.username}</p>)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MainScreen