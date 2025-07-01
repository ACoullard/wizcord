function MessageItem(message: string, isSameUser: boolean, id: string) {
    return (
            <>
                <div className="flex flex-row h-10 justify-end p-1">
                    {!isSameUser && <div className="w-1/15 h-5 center text-left"><p>UserName</p></div>}
                    <div className="w-14/15 h-5 p-l-3"><p>Message</p></div>
                </div>
                {/* TODO: Check if this is the first message, if no, put a little border thing, same as is done with servers. */}
            </>
    )
}

function MessageList() {
    let messages = [
        { content: "Hello, world!", isSameUser: false, id: "1" },
        { content: "How are you?", isSameUser: true, id: "2" },
        { content: "I'm fine, thanks!", isSameUser: false, id: "3" }
    ];

    return (
        <>
            {messages.map(msg => MessageItem(msg.content, msg.isSameUser, msg.id))}
        </>
    );
}

export default MessageList;