import React, { useState, useCallback, KeyboardEvent } from 'react';
import styles from './styles.module.css';

interface InputBarProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MAX_LENGTH = 4000;

export default function InputBar({
  onSend,
  disabled = false,
  placeholder = 'Type your question...',
}: InputBarProps): JSX.Element {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback(() => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  }, [input, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const remaining = MAX_LENGTH - input.length;
  const isOverLimit = remaining < 0;

  return (
    <div className={styles.inputBar}>
      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className={styles.input}
        rows={1}
        maxLength={MAX_LENGTH}
      />
      <div className={styles.inputActions}>
        <span
          className={`${styles.charCount} ${isOverLimit ? styles.overLimit : ''}`}
        >
          {remaining}
        </span>
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim() || isOverLimit}
          className={styles.sendButton}
          title="Send message"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
