'use client';

import { useEffect, useMemo, useState } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { motion } from 'motion/react';
import { RoomAudioRenderer, RoomContext, StartAudio } from '@livekit/components-react';
import { toastAlert } from '@/components/alert-toast';
import { OnboardingForm } from '@/components/onboarding-form';
import { SessionView } from '@/components/session-view';
import { Toaster } from '@/components/ui/sonner';
import { Welcome } from '@/components/welcome';
import useConnectionDetails from '@/hooks/useConnectionDetails';
import type { AppConfig } from '@/lib/types';

const MotionWelcome = motion.create(Welcome);
const MotionSessionView = motion.create(SessionView);

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const room = useMemo(() => new Room(), []);
  const [sessionStarted, setSessionStarted] = useState(false);
  const { startRoom } = useConnectionDetails(appConfig);

  useEffect(() => {
    const onDisconnected = () => {
      setSessionStarted(false);
    };
    const onMediaDevicesError = (error: Error) => {
      toastAlert({
        title: 'Encountered an error with your media devices',
        description: `${error.name}: ${error.message}`,
      });
    };
    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);
    room.on(RoomEvent.Disconnected, onDisconnected);
    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
    };
  }, [room]);

  useEffect(() => {
    if (sessionStarted && room.state === 'disconnected') {
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: appConfig.isPreConnectBufferEnabled,
        }),
        startRoom().then((connectionDetails) =>
          room.connect(connectionDetails.serverUrl, connectionDetails.participantToken)
        ),
      ]).catch((error) => {
        toastAlert({
          title: 'There was an error connecting to the agent',
          description: `${error.name}: ${error.message}`,
        });
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionStarted]);

  const { startButtonText } = appConfig;

  return (
    <main className="flex h-screen w-full">
      {/* Left side: Welcome/Session View (40%) */}
      <div className="relative flex h-full w-2/5 flex-col border-r">
        <MotionWelcome
          key="welcome"
          startButtonText={startButtonText}
          onStartCall={() => setSessionStarted(true)}
          disabled={sessionStarted}
          initial={{ opacity: 1 }}
          animate={{ opacity: sessionStarted ? 0 : 1 }}
          transition={{ duration: 0.5, ease: 'linear', delay: sessionStarted ? 0 : 0.5 }}
        />

        <RoomContext.Provider value={room}>
          <RoomAudioRenderer />
          <StartAudio label="Start Audio" />
          {/* --- */}
          <MotionSessionView
            key="session-view"
            appConfig={appConfig}
            disabled={!sessionStarted}
            sessionStarted={sessionStarted}
            initial={{ opacity: 0 }}
            animate={{ opacity: sessionStarted ? 1 : 0 }}
            transition={{
              duration: 0.5,
              ease: 'linear',
              delay: sessionStarted ? 0.5 : 0,
            }}
          />
        </RoomContext.Provider>
      </div>

      {/* Right side: Onboarding Form (60%) - Always visible */}
      <div className="h-full w-3/5 overflow-y-auto bg-gray-50 dark:bg-gray-900">
        <OnboardingForm />
      </div>

      <Toaster />
    </main>
  );
}
