import { useRef, useEffect } from 'react';
import { BACKEND_URL } from '@/constants';
import type { MessageData } from '@main/types';


const endpoint = new URL(`api/channel/message-stream`, BACKEND_URL);

type eventListner = (data: MessageData) => any

export function useMessageSSEListener(channelId: string | undefined, onEvent: eventListner) {
    const eventSourceRef = useRef<EventSource>(null);
    useEffect( () => {
        if (channelId == undefined) {
            return
        }
        endpoint.searchParams.set('channel', channelId)
        const eventSource = new EventSource(endpoint, {
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

