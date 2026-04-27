import { useState, useEffect } from 'react';
import ChannelList from './ChannelList';
import ChannelMessagePane from './ChannelMessagePane';
import ServerMemberList from './ServerMemberList';
import { useServerMemberSSEListener } from '@main/hooks/useSSEListener';
import { useServerDataCache } from '@main/hooks/useServerDataCache';
import type { ChannelData, ServerMemberData } from '@main/types';

type Props = {
    serverId: string
}

function ServerView({ serverId }: Props) {
    const get_server_data = useServerDataCache()

    const [channelsList, setChannelsList] = useState<ChannelData[]>([])
    const [currentChannel, setCurrentChannel] = useState<ChannelData>()
    const [userList, setUserList] = useState<ServerMemberData[]>([])

    useEffect(() => {
        console.log("Fetching server data for:", serverId)
        get_server_data(serverId)
            .then((server_data) => {
                setChannelsList(server_data.channels)
                setCurrentChannel(server_data.channels[0])
                setUserList(server_data.users)
            })
            .catch(console.error)
    }, [serverId, get_server_data])

    useServerMemberSSEListener(serverId, (member) => {
        console.log('incoming member', member)
        setUserList(prev => prev.some(u => u.id === member.id) ? prev : [...prev, member])
    })

    return (
        <>
            <div className='bg-primary border-l-3 border-l-[#5a61cc] w-1/7 flex flex-col p-b-0'>
                <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'>
                    <p>Channel List</p>
                </div>
                <div className='p-2 bg-secondary h-full overflow-y-auto'>
                    <ChannelList
                        onChannelClick={(name) => setCurrentChannel(channelsList.find(c => c.name === name))}
                        channelNames={channelsList.map(c => c.name)}
                    />
                </div>
            </div>

            {currentChannel
                ? <ChannelMessagePane channel={currentChannel} users={userList} />
                : <div className='bg-primary w-29/42' />
            }

            <ServerMemberList users={userList} />
        </>
    )
}

export default ServerView;
