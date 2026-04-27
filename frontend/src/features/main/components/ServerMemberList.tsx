import { useAuthStatusContext } from '@/contexts/AuthStatusContextProvider';
import type { ServerMemberData } from '@main/types';

type Props = {
    users: ServerMemberData[]
}

function ServerMemberList({ users }: Props) {
    const { userData } = useAuthStatusContext()

    return (
        <div className='bg-secondary w-1/6 flex flex-col'>
            <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'>
                <p>Current User</p>
            </div>
            <p className='px-4'>{userData?.username}</p>
            <div className='bg-secondary text-center flex text-highlight h-1/25 p-1 items-center justify-center border-b-3 border-b-[#5a61cc]'>
                <p>User List</p>
            </div>
            <div className='p-4'>
                {users.map(user => <p key={user.id}>{user.username}</p>)}
            </div>
        </div>
    )
}

export default ServerMemberList;
