import { useRef, useEffect } from 'react';
import type { MessageData, ServerMemberData } from '@main/types';

type messageEventListener = (data: MessageData) => void
type memberEventListener = (data: ServerMemberData) => void

export function useMessageSSEListener(channelId: string, onEvent: messageEventListener) {
    const onEventRef = useRef(onEvent);
    onEventRef.current = onEvent;

    useEffect(() => {
        const url = new URL(`api/channel/message-stream`, window.location.origin);
        url.searchParams.set('channel', channelId);
        const eventSource = new EventSource(url, { withCredentials: true });

        eventSource.onmessage = (event) => {
            const rawMessageData = JSON.parse(event.data);
            const message: MessageData = {
                id: rawMessageData.id,
                content: rawMessageData.content,
                timestamp: new Date(rawMessageData.timestamp),
                user: rawMessageData.author_id
            };
            onEventRef.current(message);
        };

        eventSource.onerror = () => {
            console.error('Message SSE error — EventSource will reconnect');
        };

        return () => {
            eventSource.close();
        };
    }, [channelId]);
}

export function useServerMemberSSEListener(serverId: string, onEvent: memberEventListener) {
    const onEventRef = useRef(onEvent);
    onEventRef.current = onEvent;

    useEffect(() => {
        const url = new URL(`api/channel/server-member-stream`, window.location.origin);
        url.searchParams.set('server', serverId);
        const eventSource = new EventSource(url, { withCredentials: true });

        eventSource.onmessage = (event) => {
            const rawMemberData = JSON.parse(event.data);
            const member: ServerMemberData = {
                id: rawMemberData.id,
                server_id: rawMemberData.server_id,
                username: rawMemberData.username
            };
            onEventRef.current(member);
        };

        eventSource.onerror = () => {
            console.error('Member SSE error — EventSource will reconnect');
        };

        return () => {
            eventSource.close();
        };
    }, [serverId]);
}
