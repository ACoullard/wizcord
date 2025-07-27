export interface ChannelData {
  id: string;
  name: string;
  creationDate: string;
}

export interface ServerData {
  id: string;
  name: string;
  channels: ChannelData[];
  users: UserData[];
}

export interface MessageData {
  id: string;
  content: string;
  user: string;
  timestamp: Date;
}

export interface UserData {
  user_id: string,
  server_id: string,
  username: string
}