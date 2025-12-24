import argparse
import abc
from models.model import Model
from bson import ObjectId



parser = argparse.ArgumentParser(prog="server_edit")
subparsers = parser.add_subparsers(dest="command", required=True)

model = Model()

class SubCommand:
    def __init__(self, name: str, help: str):
        self.name = name
        self.help = help
        self.parser = subparsers.add_parser(name, help=help)

    @abc.abstractmethod
    def execute(self, args: argparse.Namespace):
        pass

class GetUserInfo(SubCommand):
    def __init__(self):
        super().__init__("get_user_info", "Get user information by user ID")
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

class LS(SubCommand):
    def __init__(self):
        super().__init__("ls", "List out instances of objects")
        self.parser.add_argument("type", default="users", help="Type of items to list (default: users)")
        self.parser.add_argument("--server", help="Server ID to list users from")
        self.parser.add_argument("--all", action="store_true", help="List all items of the specified type")

    def execute(self, args: argparse.Namespace):
        if args.type == "users":
            if args.server is not None:
                users = model.get_user_ids_in_server(args.server)
            elif args.all:
                users = model.get_all_users()
            else:
                print("Please specify --server or --all to list users.")
                return
            
            for user in users:
                print(f"User ID: {user["_id"]}, Name: {user["username"]}, Email: {user["email"]}")

        elif args.type == "servers":
            servers = model.get_all_servers()
            for server in servers:
                print(f"Server ID: {server["_id"]}, Name: {server["name"]}")
        else:
            print(f"Unknown type: {args.type}")


active_sub_commands : list[SubCommand]= [
    GetUserInfo(),
    LS(),
]

command_name_map = {cmd.name: cmd for cmd in active_sub_commands}

def main():
    model.connect(False)

    args = parser.parse_args()

    command_name = args.command
    if args.command not in command_name_map:
        print(f"Unknown command: {command_name}")
    else:
        command = command_name_map[command_name]
        command.execute(args)

    model.close(False)

if __name__ == "__main__":
    main()