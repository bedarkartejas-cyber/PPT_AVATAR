import type { AppConfig } from './lib/types';

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Anam',
  pageTitle: 'AI Onboarding Assistant',
  pageDescription: 'Your personal AI assistant for seamless employee onboarding',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#002cf2',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#1fd5f9',
  startButtonText: 'Start Onboarding',

  agentName: 'Onboarding Assistant',
};
