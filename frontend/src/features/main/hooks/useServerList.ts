import { useState, useEffect } from 'react';

interface ServerNameTag {
  id: string;
  name: string;
}

async function getServerList(): Promise<ServerNameTag[]> {
  const response = await fetch("api/servers", { credentials: 'include' });
  if (!response.ok) {
    throw new Error("unable to fetch servers data");
  }
  return response.json();
}

export function useServerList() {
  const [serverList, setServerList] = useState<ServerNameTag[]>([]);
  const [currentServer, setCurrentServer] = useState<ServerNameTag>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;

    getServerList()
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
