import type { MessageData, ServerMemberData } from '@main/types';

interface MessageItemProps {
    username: string;
    content: string;
    isSameUser: boolean;
}

function MessageItem({content, username, isSameUser}: MessageItemProps) {
    return (
            <>
                <div className="flex flex-col justify-end p-1">
                    {!isSameUser && <div className="h-5 center text-left"><b>{username}</b></div>}
                    <div className="h-5 p-l-3"><p>{content}</p></div>
                </div>
                {/* TODO: Check if this is the first message, if no, put a little border thing, same as is done with servers. */}
            </>
    )
}

interface MessageListProps {
    messages: MessageData[]
    users: ServerMemberData[]
}

function MessageList({messages, users}: MessageListProps) {

    const userMap = users.reduce<Record<string, ServerMemberData>>((acc, user) => {
        acc[user.id] = user;
        return acc
    }, {})

    messages.sort(function(x, y){
        return x.timestamp.getTime() -  y.timestamp.getTime();
    })

    const messageItemData = []
    for (let i = 0; i < messages.length; i++) {
        let isSameUser
        if (i > 0 && messages[i].user == messages[i-1].user) {
            isSameUser = true
        } else {
            isSameUser = false
        }
        messageItemData.push(<MessageItem 
            content={messages[i].content}
            username={userMap[messages[i].user].username}
            isSameUser={isSameUser} 
            key={i}
            />
        )
    }
    return messageItemData;
}

export default MessageList;