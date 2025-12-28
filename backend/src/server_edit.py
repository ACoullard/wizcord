import argparse
import abc
from models.model import Model, AccessLevel
from bson import ObjectId



parser = argparse.ArgumentParser(prog="server_edit")
subparsers = parser.add_subparsers(dest="command", required=True)

server_parser = subparsers.add_parser("server", help="Server commands")
server_subparsers = server_parser.add_subparsers(dest="sub_command", required=True)

channel_parser = subparsers.add_parser("channel", help="Channel commands")
channel_subparsers = channel_parser.add_subparsers(dest="sub_command", required=True)

user_parser = subparsers.add_parser("user", help="User commands")
user_subparsers = user_parser.add_subparsers(dest="sub_command", required=True)

messages_parser = subparsers.add_parser("msg", help="Messages commands")
messages_subparsers = messages_parser.add_subparsers(dest="sub_command", required=True)

model = Model()

class SubCommand:
    def __init__(self, subparsers, name: str, help: str):
        self.name = name
        self.help = help
        self.parser = subparsers.add_parser(name, help=help)
        self.parser.set_defaults(execute=self.execute)

    @abc.abstractmethod
    def execute(self, args: argparse.Namespace):
        pass

class GetUserInfo(SubCommand):
    def __init__(self):
        super().__init__(subparsers, "get_user_info", "Get user information by user ID")
        self.parser.add_argument("user_id", help="ID of the user")

    def execute(self, args: argparse.Namespace):
        uid = ObjectId(args.user_id)
        user = model.get_user_by_id(uid)

        servers = model.get_viewable_server_ids(uid)
        if user:
            print(f"User ID: {user["_id"]}")
            print(f"Name: {user["username"]}")
            print(f"Email: {user["email"]}")
            print(f"Viewable Servers:")
            for server in servers:
                print(f" - Server ID: {server}")
        else:
            print(f"No user found with ID {args.user_id}")



"""
============================================================================================
User Commands
============================================================================================
"""

class UserNew(SubCommand):
    def __init__(self):
        super().__init__(user_subparsers, "new", "Add a new user to the system")
        self.parser.add_argument("username", help="Username of the new user")
        self.parser.add_argument("email", help="Email of the new user")

    def execute(self, args: argparse.Namespace):
        user_id = model.add_user(args.username, args.email)
        print(f"User added with ID: {user_id}")

class UserLS(SubCommand):
    def __init__(self):
        super().__init__(user_subparsers, "ls", "List users")
        self.parser.add_argument("--server", help="Server ID to list users from")
        self.parser.add_argument("--all", action="store_true", help="List all users")

    def execute(self, args: argparse.Namespace):
        if args.server is not None:
            users = model.get_user_ids_in_server(ObjectId(args.server))
        elif args.all:
            users = model.get_all_users()
        else:
            print("Please specify --server or --all to list users.")
            return
        
        for user in users:
            print(f"User ID: {user["_id"]}, Name: {user["username"]}, Email: {user["email"]}")

"""
============================================================================================
Server Commands
============================================================================================
"""

class ServerNew(SubCommand):
    def __init__(self):
        super().__init__(server_subparsers, "new", "Create a new server")
        self.parser.add_argument("name", help="Name of the new server")

    def execute(self, args: argparse.Namespace):
        server_id = model.add_server(args.name)
        print(f"Server created with ID: {server_id}")

class ServerLS(SubCommand):
    def __init__(self):
        super().__init__(server_subparsers, "ls", "List all servers")

    def execute(self, args: argparse.Namespace):
        servers = model.get_all_servers()
        for server in servers:
            print(f"Server ID: {server["_id"]}, Name: {server["name"]}")

class ServerAddUser(SubCommand):
    def __init__(self):
        super().__init__(server_subparsers, "add_user", "Add a user to a server")
        self.parser.add_argument("user_id", help="ID of the user")
        self.parser.add_argument("server_id", help="ID of the server")

    def execute(self, args: argparse.Namespace):
        uid = ObjectId(args.user_id)
        sid = ObjectId(args.server_id)
        member_id = model.add_user_to_server(uid, sid)
        print(f"User {uid} added to server {sid}. Membership ID: {member_id}")


class ServerAddChannel(SubCommand):
    def __init__(self):
        super().__init__(server_subparsers, "add_channel", "Add a channel to a server")
        self.parser.add_argument("server_id", help="ID of the server")
        self.parser.add_argument("name", help="Name of the channel")

    def execute(self, args: argparse.Namespace):
        sid = ObjectId(args.server_id)
        channel_id = model.add_channel(args.name, sid)
        print(f"Channel '{args.name}' added to server {sid}. Channel ID: {channel_id}")


"""
============================================================================================
Channel Commands
============================================================================================
"""

class ChannelNew(SubCommand):
    def __init__(self):
        super().__init__(channel_subparsers, "new", "Create a new channel")
        self.parser.add_argument("server_id", help="ID of the server")
        self.parser.add_argument("name", help="Name of the channel")

    def execute(self, args: argparse.Namespace):
        sid = ObjectId(args.server_id)

        channel_id = model.add_channel(args.name, sid)
        print(f"Channel '{args.name}' created in server {sid}. Channel ID: {channel_id}")

class ChannelLS(SubCommand):
    def __init__(self):
        super().__init__(channel_subparsers, "ls", "List channels in a server")
        self.parser.add_argument("--server", required=True, help="Server ID to list channels from")

    def execute(self, args: argparse.Namespace):
        channels = model.get_channels_data_by_server(ObjectId(args.server))
        for channel in channels:
            print(f"Channel ID: {channel["_id"]}, Name: {channel["name"]}, Creation Time: {channel["creation_date"]}")


class ChannelAddUser(SubCommand):
    def __init__(self):
        super().__init__(channel_subparsers, "add_user", "Add a user to a channel")
        self.parser.add_argument("user_id", help="ID of the user")
        self.parser.add_argument("channel_id", help="ID of the channel")
        self.parser.add_argument("access_level", choices=["VIEW", "POST"], help="Access level (VIEW or POST)")

    def execute(self, args: argparse.Namespace):
        uid = ObjectId(args.user_id)
        cid = ObjectId(args.channel_id)
        level = AccessLevel[args.access_level]

        member_id = model.add_user_to_channel(uid, cid, level)
        print(f"User {uid} added to channel {cid} with access {level.name}. Membership ID: {member_id}")


"""
============================================================================================
Message Commands
============================================================================================
"""

class MessageLS(SubCommand):
    def __init__(self):
        super().__init__(messages_subparsers, "ls", "List messages")
        self.parser.add_argument("--channel", help="Filter messages by channel ID")
        self.parser.add_argument("--user", help="Filter messages by user ID")

    def execute(self, args: argparse.Namespace):
        channel_id = ObjectId(args.channel) if args.channel else None
        user_id = ObjectId(args.user) if args.user else None

        messages = model.get_messages_filtered(channel_id=channel_id, user_id=user_id, show_hidden=True)
        
        for message in messages:
            print(f"Msg ID: {message["_id"]}, Content: {message["content"][:50]}, Author ID: {message["author_id"]}, Channel ID: {message["channel_id"]}, Timestamp: {message["timestamp"]}")

class MessageHide(SubCommand):
    def __init__(self):
        super().__init__(messages_subparsers, "hide", "Hide a message")
        self.parser.add_argument("message_id", help="ID of the message to hide")

    def execute(self, args: argparse.Namespace):
        msg_id = ObjectId(args.message_id)
        success = model.hide_message(msg_id)
        if success:
            print(f"Message {msg_id} has been hidden.")
        else:
            print(f"Message {msg_id} not found.")

active_sub_commands : list[SubCommand]= [
    GetUserInfo(),
    UserNew(),
    UserLS(),
    ServerNew(),
    ServerLS(),
    ServerAddUser(),
    ServerAddChannel(),
    ChannelNew(),
    ChannelLS(),
    ChannelAddUser(),
    MessageLS(),
    MessageHide(),
]


def main():
    model.connect(False)

    args = parser.parse_args()

    if hasattr(args, 'execute'):
        try:
            args.execute(args)
        except Exception as e:
            print(f"Error: {type(e)} {e}")
    else:
        parser.print_help()

    model.close(False)

if __name__ == "__main__":
    main() 