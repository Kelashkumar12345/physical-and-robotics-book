import React from 'react';
import MessageList from './MessageList';
import InputBar from './InputBar';
import type { Message } from './index';
import styles from './styles.module.css';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  questionsRemaining: number;
  selectedContext: string | null;
  error: string | null;
  onSend: (message: string) => void;
  onClose: () => void;
  onReset: () => void;
  onClearContext: () => void;
}

export default function ChatWindow({
  messages,
  isLoading,
  questionsRemaining,
  selectedContext,
  error,
  onSend,
  onClose,
  onReset,
  onClearContext,
}: ChatWindowProps): JSX.Element {
  return (
    <div className={styles.window}>
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          <span>Physical AI Assistant</span>
          <span className={styles.questionsRemaining}>
            {questionsRemaining} questions left
          </span>
        </div>
        <div className={styles.headerActions}>
          <button
            onClick={onReset}
            className={styles.resetButton}
            title="Start new session"
          >
            ↻
          </button>
          <button
            onClick={onClose}
            className={styles.closeButton}
            title="Close chat"
          >
            ✕
          </button>
        </div>
      </header>

      {selectedContext && (
        <div className={styles.contextBanner}>
          <span className={styles.contextLabel}>Asking about:</span>
          <span className={styles.contextText}>
            "{selectedContext.slice(0, 100)}
            {selectedContext.length > 100 ? '...' : ''}"
          </span>
          <button onClick={onClearContext} className={styles.clearContext}>
            ✕
          </button>
        </div>
      )}

      <MessageList messages={messages} isLoading={isLoading} />

      {error && <div className={styles.error}>{error}</div>}

      <InputBar
        onSend={onSend}
        disabled={isLoading || questionsRemaining === 0}
        placeholder={
          questionsRemaining === 0
            ? 'Session limit reached. Reset to continue.'
            : 'Ask about Physical AI, ROS 2, Isaac...'
        }
      />
    </div>
  );
}
