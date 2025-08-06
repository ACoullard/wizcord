import type { MessageData, UserData } from '@main/types';

interface MessageItemProps {
    username: string;
    content: string;
    isSameUser: boolean;
}

function MessageItem({content, username, isSameUser}: MessageItemProps) {
    return (
            <>
                <div className="flex flex-row h-10 justify-end p-1">
                    {!isSameUser && <div className="w-1/15 h-5 center text-left"><p>{username}</p></div>}
                    <div className="w-14/15 h-5 p-l-3"><p>{content}</p></div>
                </div>
                {/* TODO: Check if this is the first message, if no, put a little border thing, same as is done with servers. */}
            </>
    )
}

interface MessageListProps {
    messages: MessageData[]
    users: UserData[]
}

function MessageList({messages, users}: MessageListProps) {

    const userMap = users.reduce<Record<string, UserData>>((acc, user) => {
        acc[user.user_id] = user;
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