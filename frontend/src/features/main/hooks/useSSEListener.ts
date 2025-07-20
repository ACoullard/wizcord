import { useRef, useEffect } from 'react';
import { BACKEND_URL } from '@/constants';
import type { MessageData } from '@main/types';


const endpoint = new URL(`api/channel/message-stream`, BACKEND_URL);

type eventListner = (data: MessageData) => any

export function useMessageSSEListener(channelId: string | undefined, onEvent: eventListner) {
    const eventSourceRef = useRef<EventSource>(null);
    console.log("got here 1", channelId)

    useEffect( () => {
        if (channelId == undefined) {
            console.log("got here 2")
            return
        }
        endpoint.searchParams.set('channel', channelId)
        const eventSource = new EventSource(endpoint, {
            withCredentials: true,
            });
        console.log("gh 3")
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log(message)
            onEvent(message);
        };

        // tear down function. useEffect works like that ig
        return () => {
            eventSource.close();
        }
    }, [onEvent, channelId])
    
};

