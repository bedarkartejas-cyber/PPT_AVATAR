'use client';

import React, { useEffect, useState } from 'react';
import { Track } from 'livekit-client';
import { AnimatePresence, motion } from 'motion/react';
import {
  type AgentState,
  type ReceivedChatMessage,
  useRoomContext,
  useTracks,
  useVoiceAssistant,
} from '@livekit/components-react';
import { toastAlert } from '@/components/alert-toast';
import { BrowserControlListener } from '@/components/browser-control-listener';
import { AgentControlBar } from '@/components/livekit/agent-control-bar/agent-control-bar';
import { ChatEntry } from '@/components/livekit/chat/chat-entry';
import { ChatMessageView } from '@/components/livekit/chat/chat-message-view';
import { MediaTiles } from '@/components/livekit/media-tiles';
import useChatAndTranscription from '@/hooks/useChatAndTranscription';
import { useDebugMode } from '@/hooks/useDebug';
import type { AppConfig } from '@/lib/types';
import { cn } from '@/lib/utils';

function isAgentAvailable(agentState: AgentState) {
  return agentState == 'listening' || agentState == 'thinking' || agentState == 'speaking';
}

interface SessionViewProps {
  appConfig: AppConfig;
  disabled: boolean;
  sessionStarted: boolean;
}

export const SessionView = ({
  appConfig,
  disabled,
  sessionStarted,
  ref,
}: React.ComponentProps<'div'> & SessionViewProps) => {
  const { state: agentState } = useVoiceAssistant();
  const [chatOpen, setChatOpen] = useState(false);
  const { messages, send } = useChatAndTranscription();
  const room = useRoomContext();
  const [screenShareTrack] = useTracks([Track.Source.ScreenShare]);
  const isScreenShareActive = screenShareTrack && !screenShareTrack.publication.isMuted;

  useDebugMode({
    enabled: process.env.NODE_ENV !== 'production',
  });

  async function handleSendMessage(message: string) {
    await send(message);
  }

  // Auto-launch screen share when session starts
  useEffect(() => {
    if (sessionStarted && room.state === 'connected') {
      const startScreenShare = async () => {
        try {
          // Small delay to let the UI settle
          await new Promise((resolve) => setTimeout(resolve, 1000));

          // Check if screen share is already active
          const localParticipant = room.localParticipant;
          if (!localParticipant.isScreenShareEnabled) {
            console.log('🖥️ Auto-launching screen share...');
            await localParticipant.setScreenShareEnabled(true);
            console.log('✅ Screen share started');
          }
        } catch (error) {
          console.warn('Could not auto-start screen share:', error);
          toastAlert({
            title: 'Screen share required',
            description: <p>Please enable screen share so Maya can see the form.</p>,
          });
        }
      };
      startScreenShare();
    }
  }, [sessionStarted, room]);

  useEffect(() => {
    if (sessionStarted) {
      const timeout = setTimeout(() => {
        if (!isAgentAvailable(agentState)) {
          const reason =
            agentState === 'connecting'
              ? 'Agent did not join the room. '
              : 'Agent connected but did not complete initializing. ';

          toastAlert({
            title: 'Session ended',
            description: (
              <p className="w-full">
                {reason}
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://docs.livekit.io/agents/start/voice-ai/"
                  className="whitespace-nowrap underline"
                >
                  See quickstart guide
                </a>
                .
              </p>
            ),
          });
          room.disconnect();
        }
      }, 20_000);

      return () => clearTimeout(timeout);
    }
  }, [agentState, sessionStarted, room]);

  const { supportsChatInput, supportsVideoInput, supportsScreenShare } = appConfig;
  const capabilities = {
    supportsChatInput,
    supportsVideoInput,
    supportsScreenShare,
  };

  return (
    <section
      ref={ref}
      inert={disabled}
      className={cn(
        'absolute inset-0 overflow-hidden opacity-0',
        // prevent page scrollbar
        // when !chatOpen due to 'translate-y-20'
        !chatOpen && 'max-h-full'
      )}
    >
      {/* Browser control listener - receives commands from AI agent */}
      <BrowserControlListener />

      <ChatMessageView
        className={cn(
          'mx-auto h-full w-full max-w-2xl px-3 pt-32 pb-40 transition-[opacity,translate] duration-300 ease-out md:px-0 md:pt-36 md:pb-48',
          chatOpen ? 'translate-y-0 opacity-100 delay-200' : 'translate-y-20 opacity-0'
        )}
      >
        <div className="space-y-3 whitespace-pre-wrap">
          <AnimatePresence>
            {messages.map((message: ReceivedChatMessage) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 1, height: 'auto', translateY: 0.001 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              >
                <ChatEntry hideName key={message.id} entry={message} />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </ChatMessageView>

      <div className="bg-background mp-12 absolute top-0 right-0 left-0 h-32 md:h-36">
        {/* Screen share indicator */}
        {isScreenShareActive && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-4 left-1/2 z-10 -translate-x-1/2"
          >
            <div className="flex items-center gap-2 rounded-full border border-green-500 bg-green-500/10 px-4 py-2 backdrop-blur-sm">
              <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
              <span className="text-sm font-medium text-green-700 dark:text-green-300">
                Screen Sharing Active - AI can see your screen
              </span>
            </div>
          </motion.div>
        )}
        {/* skrim */}
        <div className="from-background absolute bottom-0 left-0 h-12 w-full translate-y-full bg-gradient-to-b to-transparent" />
      </div>

      <MediaTiles chatOpen={chatOpen} />

      <div className="bg-background absolute right-0 bottom-0 left-0 z-50 px-3 pt-2 pb-3 md:px-4 md:pb-4">
        <motion.div
          key="control-bar"
          initial={{ opacity: 0, translateY: '100%' }}
          animate={{
            opacity: sessionStarted ? 1 : 0,
            translateY: sessionStarted ? '0%' : '100%',
          }}
          transition={{ duration: 0.3, delay: sessionStarted ? 0.5 : 0, ease: 'easeOut' }}
        >
          <div className="relative z-10 mx-auto w-full">
            {appConfig.isPreConnectBufferEnabled && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{
                  opacity: sessionStarted && messages.length === 0 ? 1 : 0,
                  transition: {
                    ease: 'easeIn',
                    delay: messages.length > 0 ? 0 : 0.8,
                    duration: messages.length > 0 ? 0.2 : 0.5,
                  },
                }}
                aria-hidden={messages.length > 0}
                className={cn(
                  'absolute inset-x-0 -top-12 text-center',
                  sessionStarted && messages.length === 0 && 'pointer-events-none'
                )}
              >
                <p className="animate-text-shimmer inline-block !bg-clip-text text-sm font-semibold text-transparent">
                  Agent is listening, ask it a question
                </p>
              </motion.div>
            )}

            <AgentControlBar
              capabilities={capabilities}
              onChatOpenChange={setChatOpen}
              onSendMessage={handleSendMessage}
            />
          </div>
          {/* skrim */}
          <div className="from-background border-background absolute top-0 left-0 h-12 w-full -translate-y-full bg-gradient-to-t to-transparent" />
        </motion.div>
      </div>
    </section>
  );
};
