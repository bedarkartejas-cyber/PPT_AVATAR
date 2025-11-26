import { useCallback, useState } from 'react';
import { ConnectionDetails } from '@/app/api/connection-details/route';
import { AppConfig } from '@/lib/types';

export default function useConnectionDetails(appConfig: AppConfig) {
  const [connectionDetails, setConnectionDetails] = useState<ConnectionDetails | null>(null);

  const fetchConnectionDetails = useCallback(async () => {
    setConnectionDetails(null);

    const url = new URL(
      process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? '/api/connection-details',
      window.location.origin
    );

    const res = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Sandbox-Id': appConfig.sandboxId ?? '',
      },
      body: JSON.stringify({
        room_config: appConfig.agentName
          ? { agents: [{ agent_name: appConfig.agentName }] }
          : undefined,
      }),
    });

    if (!res.ok) {
      throw new Error('Error fetching connection details');
    }

    const data: ConnectionDetails = await res.json();
    setConnectionDetails(data);
    return data;
  }, [appConfig]);

  return {
    connectionDetails,
    startRoom: fetchConnectionDetails,
  };
}
