function ServerItem(Server: string) {
    return (
        <>
            <div className="flex flex-row h-1/30 px-2 items-center justify-center">
                <div className='w-4 h-full flex items-center justify-center mr-1'><p>#</p></div>
                <div className='w-full h-full flex items-center'>{Server}</div>
            </div>
            <hr className="w-14/15 h-0.5 my-1 message-bg border-0 flex rounded-3xl mb-1.5 mx-auto"/>
            {/* TODO: Check if this is the first message, if no, put a little border thing, same as is done with servers. */}
        </>
    );
}

function ServerList() {
    let items = [
        'School Stumped',
        'Wizards Unite',
        'Magic Mayhem'
    ]
    
    return (
        <>
            {items.length === 0 && <p>No items found</p>}
            {items.map(item => ServerItem(item))}
            
        </>
    );
}

export default ServerList;