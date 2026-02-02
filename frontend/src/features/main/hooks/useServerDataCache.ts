import type { ServerData } from '@main/types';
import { useRef, useCallback } from 'react';



async function get_server_data(serverId: string): Promise<ServerData> {
  const endpoint = `api/server-data/${serverId}`
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
  // console.log("useServerDataCache called");
  const serverDataCache = useRef<Record<string, ServerCacheEntry>>({})

  const get_data_promise = useCallback((serverId: string): Promise<ServerData> => {
    const cached = serverDataCache.current[serverId];
    // if already have data, return it as a promise
    if (cached?.data) {
      return Promise.resolve(cached.data);
    }
    
    // if a fetch is already in progress, return the existing promise
    if (cached?.promise) {
      return cached.promise;
    }

    // otherwise, start a new fetch
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
  }, [])


  return get_data_promise;
}