import { useState, useEffect } from 'react';
import { BACKEND_URL } from '@/constants';

interface ServerNameTag {
  id: string;
  name: string;

}

async function getServerList(): Promise<ServerNameTag[]>{
  const endpoint = new URL("api/servers", BACKEND_URL)
  try {
    const responce =  await fetch(endpoint, {credentials: 'include'})
    if (!responce.ok) {
      throw new Error("unable to fetch servers data")
    }

    const json = await responce.json()
    console.log(json)
    return json
  } catch (error) {
    console.error(error);
    return []
  }
}

async function getCurrentUser() {
  const endpoint = new URL("api/login/current-user", BACKEND_URL)
  const responce = await fetch(endpoint, {
    credentials: 'include'
  })
  if (!responce.ok) {
      throw new Error("unable to fetch current user")
    }
  const json = await responce.json()
  return json
}

export function useServerList() {
  const [serverList, setServerList] = useState<ServerNameTag[]>([]);
  const [currentServer, setCurrentServer] = useState<ServerNameTag>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;

    getCurrentUser()
      .then(() => getServerList())
      .then((res) => {
        if (!mounted) return;
        setServerList(res);
        if (res.length > 0) {
          setCurrentServer(res[0]);
        }
        setIsLoading(false);
      })
      .catch((err) => {
        if (!mounted) return;
        console.error(err);
        setError(err);
        setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return { serverList, currentServer, setCurrentServer, isLoading, error };
}