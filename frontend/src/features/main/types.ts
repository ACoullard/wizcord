export interface ChannelData {
  id: string;
  name: string;
  creationDate: string;
}

export interface ServerData {
  id: string;
  name: string;
  channels: ChannelData[];
  users: ServerMemberData[];
}

export interface MessageData {
  id: string;
  content: string;
  user: string;
  timestamp: Date;
}

export interface ServerMemberData {
  id: string,
  server_id: string,
  username: string
}

export interface UserData {
  id: string;
  username: string;
}