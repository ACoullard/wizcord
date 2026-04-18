import { useRef, useEffect } from 'react';
import type { MessageData, ServerMemberData } from '@main/types';


const messageEndpoint = new URL(`api/channel/message-stream`, window.location.origin);
const serverMemberEndpoint = new URL(`api/channel/server-member-stream`, window.location.origin);

type messageEventListner = (data: MessageData) => any
type memberEventListner = (data: ServerMemberData) => any

export function useMessageSSEListener(channelId: string | undefined, onEvent: messageEventListner) {
    const eventSourceRef = useRef<EventSource>(null);
    useEffect( () => {
        if (channelId == undefined) {
            return
        }
        messageEndpoint.searchParams.set('channel', channelId)
        const eventSource = new EventSource(messageEndpoint, {
            withCredentials: true,
            });
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const rawMessageData = JSON.parse(event.data);
            const message: MessageData = {
                id: rawMessageData.id,
                content: rawMessageData.content,
                timestamp: new Date(rawMessageData.timestamp),
                user: rawMessageData.author_id
            } 
            console.log(message)

            onEvent(message);
        };

        // tear down function. useEffect works like that ig
        return () => {
            eventSource.close();
        }
    }, [onEvent, channelId])
    
};

export function useServerMemberSSEListener(serverId: string | undefined, onEvent: memberEventListner) {
    const eventSourceRef = useRef<EventSource>(null);
    useEffect( () => {
        if (serverId == undefined) {
            return
        }
        serverMemberEndpoint.searchParams.set('server', serverId)
        const eventSource = new EventSource(serverMemberEndpoint, {
            withCredentials: true,
            });
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const rawMemberData = JSON.parse(event.data);
            const member: ServerMemberData = {
                id: rawMemberData.id,
                server_id: rawMemberData.server_id,
                username: rawMemberData.username
            }
            console.log('server member event', member)

            onEvent(member);
        };

        return () => {
            eventSource.close();
        }
    }, [onEvent, serverId])
}

