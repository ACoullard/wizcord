import { useState, useRef, useEffect, useLayoutEffect } from 'react';
import MessageList from './MessageList';
import { useMessageSSEListener } from '@main/hooks/useSSEListener';
import type { ChannelData, MessageData, ServerMemberData } from '@main/types';
import TextareaAutosize from 'react-textarea-autosize';

async function getMessages(channelId: string): Promise<MessageData[]> {
    const endpoint = new URL(`api/channel/${channelId}`, window.location.origin);
    endpoint.searchParams.set("limit", "100");
    const response = await fetch(endpoint, { credentials: 'include' });
    if (!response.ok) throw new Error("unable to fetch message data");
    const json = await response.json();
    return json["data"].map((message: { id: string; content: string; timestamp: string; author_id: string }) => ({
        id: message.id,
        content: message.content,
        timestamp: new Date(message.timestamp),
        user: message.author_id
    }));
}

async function postMessage(message: string, channelId: string) {
    const response = await fetch(`api/channel/${channelId}/post`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: message })
    });
    return response.ok;
}

const SCROLL_STICK_THRESHOLD_PX = 64;

function mergeMessages(previous: MessageData[], fetched: MessageData[]): MessageData[] {
    const byId = new Map(previous.map(message => [message.id, message]));
    for (const message of fetched) {
        byId.set(message.id, message);
    }
    return [...byId.values()];
}

type Props = {
    channel: ChannelData
    users: ServerMemberData[]
}

function ChannelMessagePane({ channel, users }: Props) {
    const [messagesList, setMessagesList] = useState<MessageData[]>([]);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const scrollContainer = useRef<HTMLDivElement>(null);
    const stickToBottom = useRef(true);

    useEffect(() => {
        stickToBottom.current = true;
        getMessages(channel.id).then(data => setMessagesList([...data]));
    }, [channel.id]);

    useLayoutEffect(() => {
        if (stickToBottom.current && scrollContainer.current) {
            scrollContainer.current.scrollTop = scrollContainer.current.scrollHeight;
        }
    }, [messagesList]);

    function handleScroll() {
        const container = scrollContainer.current;
        if (!container) return;
        const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
        stickToBottom.current = distanceFromBottom <= SCROLL_STICK_THRESHOLD_PX;
    }

    useMessageSSEListener(
        channel.id,
        (data) => {
            setMessagesList(prev => prev.some(m => m.id === data.id) ? prev : [...prev, data]);
        },
        () => {
            getMessages(channel.id)
                .then(data => setMessagesList(prev => mergeMessages(prev, data)))
                .catch(console.error);
        }
    );

    function handleMessageSubmit(event: React.KeyboardEvent<HTMLTextAreaElement>) {
        if (event.key === "Enter" && !event.shiftKey && inputRef.current) {
            event.preventDefault();
            const text = inputRef.current.value.trim();
            if (!text) return;
            postMessage(text, channel.id).then((succeeded) => {
                if (succeeded && inputRef.current) inputRef.current.value = "";
                else console.error("message failed to send");
            });
        }
    }

    return (
        <div className='bg-primary w-29/42 flex flex-col p-2'>
            <div className='flex-grow relative'>
                <div ref={scrollContainer} onScroll={handleScroll} className='overflow-y-auto h-full w-full absolute py-4'>
                    <MessageList messages={messagesList} users={users} />
                </div>
            </div>
            <div className='bg-tertiary min-h-1/18 mt-auto rounded-4xl m-2 flex flex-row items-center
                shadow-[0_0_16px_rgba(0,255,255,0.5)]
                hover:shadow-[0_0_18px_rgba(0,255,255,0.7)]
                focus-within:shadow-[0_0_20px_#00FFFF]
                hover:focus-within:shadow-[0_0_23px_#00FFFF]
                transition duration-400 ease-in-out'>
                <TextareaAutosize
                    ref={inputRef}
                    maxRows={8}
                    className="flex-grow py-2 px-5 break-all resize-none overflow-y-hidden message-text leading-tight focus:outline-none focus:shadow-outline placeholder-pixel"
                    id="input"
                    placeholder="Cast your spells here!"
                    autoCorrect='off'
                    autoComplete='off'
                    data-lpignore='true'
                    onKeyDown={handleMessageSubmit}
                />
            </div>
        </div>
    );
}

export default ChannelMessagePane;
