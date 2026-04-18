from api.shared_resources import model
from observers import server_members_observers, ServerMembersObserver
from bson import ObjectId

# Choose an existing server or create a new one
server_id = model.add_server('sse-test-server')
user_id = model.add_user('sse-test-user', 'sse@example.com')

# Ensure an observer exists and add a listener
server_id_str = str(server_id)
if server_id_str not in server_members_observers:
    server_members_observers[server_id_str] = ServerMembersObserver()
observer = server_members_observers[server_id_str]
listener = observer.add_listener()

# Add user to server (model does NOT publish; simulate API-level publish)
member_id = model.add_user_to_server(user_id, server_id)
print('member id:', member_id)

# Simulate API-level publish (only if observer exists)
observer = server_members_observers.get(server_id_str)
if observer is not None:
    observer.publish(str(user_id), server_id_str, 'sse-test-user')

# Retrieve event from listener
event = listener.retrieve_update()
print('event received:', event)
