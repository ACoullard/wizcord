import { BACKEND_URL } from '@/constants';

const endpoint = new URL(`api/stream`, BACKEND_URL);
const eventSource = new EventSource(endpoint);
console.log("did this")

type eventListner = (event: MessageEvent) => any

export function useSSEListener(eventName: string, onEvent: eventListner) {
    eventSource.addEventListener(eventName, onEvent)
};

