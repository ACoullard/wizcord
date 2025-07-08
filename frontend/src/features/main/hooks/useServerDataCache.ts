import type { ServerData } from '@main/types';
import { useRef } from 'react';

import { BACKEND_URL } from '@/constants';


async function get_server_data(serverId: string): Promise<ServerData> {
  const baseEndpoint = new URL("api/server-data/", BACKEND_URL)
  const endpoint = new URL(serverId, baseEndpoint)
  try {
    const responce =  await fetch(endpoint, {
      credentials: "include"
    })
    if (!responce.ok) {
      throw new Error(`unable to fetch server ${serverId} data`)
    }

    const json = await responce.json()
    return json
  } catch (error) {
    console.error(error);
    throw error
  }
}

type ServerCacheEntry = {
  data?: ServerData;
  promise?: Promise<ServerData>;
};

export function useServerDataCache() {
  const serverDataCache = useRef<Record<string, ServerCacheEntry>>({})
  
  function get_data(serverId: string): Promise<ServerData> {
    const cached = serverDataCache.current[serverId];
    if (cached?.data) {
      return Promise.resolve(cached.data);
    }
    
    if (cached?.promise) {
      return cached.promise;
    }

    const promise = get_server_data(serverId).then((res) => {
      console.log("Server data fetched:", res);
      serverDataCache.current[serverId] = { data: res };
      return res;
    }).catch((error) => {
      delete serverDataCache.current[serverId];
      throw error;
    });

    serverDataCache.current[serverId] = { promise };
    
    return promise;
  }


  return get_data 
}