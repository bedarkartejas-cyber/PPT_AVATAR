'use client';

import { useDataChannel } from '@livekit/components-react';

interface BrowserCommand {
  type: 'fill_field' | 'click';
  field?: string;
  value?: string;
  element?: string;
}

export function BrowserControlListener() {
  useDataChannel('browser-control', (msg) => {
    try {
      const command: BrowserCommand = JSON.parse(new TextDecoder().decode(msg.payload));
      console.log('🤖 Command:', command);

      switch (command.type) {
        case 'fill_field':
          if (command.field && command.value) {
            handleFillField(command.field, command.value);
          }
          break;
        case 'click':
          if (command.element) handleClick(command.element);
          break;
      }
    } catch (error) {
      console.error('Failed to parse command:', error);
    }
  });

  return null;
}

function handleFillField(fieldIdentifier: string, value: string) {
  console.log(`✍️ Filling "${fieldIdentifier}" with "${value}"`);

  const field = findFormField(fieldIdentifier);
  if (!field) {
    console.warn(`❌ Field not found: ${fieldIdentifier}`);
    showNotification(`Could not find field: ${fieldIdentifier}`, 'error');
    return;
  }

  if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement) {
    // Set value and trigger React state update
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(field, value);

    field.dispatchEvent(new Event('input', { bubbles: true }));
    field.dispatchEvent(new Event('change', { bubbles: true }));

    highlightElement(field, '✓ AI filled');
    console.log(`✅ Filled: ${fieldIdentifier}`);
  } else if (field instanceof HTMLSelectElement) {
    field.value = value;
    field.dispatchEvent(new Event('change', { bubbles: true }));
    highlightElement(field, '✓ AI selected');
  }
}

function findFormField(identifier: string): HTMLElement | null {
  const normalized = identifier.toLowerCase().trim();

  // 1. Find by label text
  for (const label of document.querySelectorAll('label')) {
    const text = label.textContent?.toLowerCase().trim() || '';
    if (text.includes(normalized) || normalized.includes(text)) {
      const forAttr = label.getAttribute('for');
      if (forAttr) {
        const input = document.getElementById(forAttr);
        if (input) return input;
      }
      const input = label.querySelector('input, textarea, select');
      if (input) return input as HTMLElement;
    }
  }

  // 2. Find by placeholder, name, or id
  const selectors = [
    `input[placeholder*="${identifier}" i]`,
    `input[name*="${identifier}" i]`,
    `input[id*="${identifier}" i]`,
    `textarea[placeholder*="${identifier}" i]`,
    `select[name*="${identifier}" i]`,
  ];

  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el) return el as HTMLElement;
  }

  // 3. Find by parent text
  for (const input of document.querySelectorAll('input, textarea, select')) {
    const parentText = input.parentElement?.textContent?.toLowerCase() || '';
    if (parentText.includes(normalized)) return input as HTMLElement;
  }

  return null;
}

function handleClick(elementDescription: string) {
  console.log(`👆 Clicking: ${elementDescription}`);

  const element = findClickableElement(elementDescription);
  if (!element) {
    console.warn(`❌ Element not found: ${elementDescription}`);
    showNotification(`Could not find: ${elementDescription}`, 'error');
    return;
  }

  highlightElement(element, '✓ AI clicked');

  setTimeout(() => {
    // Check for navigation data attribute
    const navTarget = element.getAttribute('data-nav');
    if (navTarget) {
      const win = window as unknown as { goToStep?: (step: string) => void };
      if (win.goToStep) {
        win.goToStep(navTarget);
        console.log(`✅ Navigated to: ${navTarget}`);
        showNotification(`Navigated to ${navTarget}`, 'success');
        return;
      }
    }

    // Check for nav button ID
    if (element.id?.startsWith('nav-')) {
      const step = element.id.replace('nav-', '').replace('-restart', '').replace('-back', '');
      const win = window as unknown as { goToStep?: (step: string) => void };
      if (win.goToStep) {
        win.goToStep(step);
        console.log(`✅ Navigated to: ${step}`);
        showNotification(`Navigated to ${step}`, 'success');
        return;
      }
    }

    // Fallback: direct click
    element.classList.remove('pointer-events-none');
    if (element instanceof HTMLButtonElement || element instanceof HTMLAnchorElement) {
      element.click();
      console.log(`✅ Clicked: ${elementDescription}`);
      showNotification(`Clicked "${elementDescription}"`, 'success');
    }
  }, 300);
}

function findClickableElement(description: string): HTMLElement | null {
  const normalized = description.toLowerCase().trim();

  // Priority: form buttons, then nav buttons, then all buttons
  const buttonGroups = [
    document.querySelectorAll('form button, [class*="form"] button'),
    document.querySelectorAll('button[data-nav], button[id^="nav-"]'),
    document.querySelectorAll('button'),
    document.querySelectorAll('a, input[type="submit"], [role="button"]'),
  ];

  for (const buttons of buttonGroups) {
    for (const el of buttons) {
      const text = el.textContent?.toLowerCase().trim() || '';
      const ariaLabel = el.getAttribute('aria-label')?.toLowerCase() || '';
      if (
        text.includes(normalized) ||
        normalized.includes(text) ||
        ariaLabel.includes(normalized)
      ) {
        return el as HTMLElement;
      }
    }
  }

  return null;
}

function highlightElement(element: HTMLElement, message: string) {
  const original = { outline: element.style.outline, bg: element.style.backgroundColor };

  element.style.outline = '3px solid #4CAF50';
  element.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';

  const indicator = document.createElement('div');
  indicator.innerHTML = message;
  indicator.style.cssText = `
    position: absolute;
    background: #4CAF50;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    z-index: 1000;
    pointer-events: none;
    white-space: nowrap;
  `;

  const rect = element.getBoundingClientRect();
  indicator.style.top = `${rect.top + window.scrollY - 30}px`;
  indicator.style.left = `${rect.left + window.scrollX}px`;
  document.body.appendChild(indicator);

  setTimeout(() => {
    element.style.outline = original.outline;
    element.style.backgroundColor = original.bg;
    indicator.remove();
  }, 2000);
}

function showNotification(message: string, type: 'success' | 'error' | 'info' = 'info') {
  const colors = {
    success: { bg: '#4CAF50', icon: '✓' },
    error: { bg: '#f44336', icon: '✗' },
    info: { bg: '#2196F3', icon: 'ℹ' },
  };

  const { bg, icon } = colors[type];

  const notification = document.createElement('div');
  notification.innerHTML = `${icon} ${message}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${bg};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    font-weight: 600;
    animation: slideIn 0.3s ease-out;
  `;
  document.body.appendChild(notification);

  setTimeout(() => notification.remove(), 3000);
}

// Add CSS animations
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
}
