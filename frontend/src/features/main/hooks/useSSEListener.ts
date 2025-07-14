const eventSource = new EventSource("http://localhost:3000/events");
console.log("did this")

type eventListner = (event: MessageEvent) => any

export function useSSEListener(eventName: string, onEvent: eventListner) {
    eventSource.addEventListener(eventName, onEvent)
};