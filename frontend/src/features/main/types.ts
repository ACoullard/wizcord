export interface ChannelData {
  id: string;
  name: string;
  creationDate: string;
}

export interface ServerData {
  id: string;
  name: string;
  channels: ChannelData[];
  users: string[];
}

export interface MessageData {
  id: string;
  content: string;
  user: string;
  timestamp: Date;
}
