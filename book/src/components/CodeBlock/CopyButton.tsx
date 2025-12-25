import React, { useState, useCallback } from 'react';
import styles from './styles.module.css';

interface CopyButtonProps {
  code: string;
}

export default function CopyButton({ code }: CopyButtonProps): JSX.Element {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  }, [code]);

  return (
    <button
      className={styles.copyButton}
      onClick={handleCopy}
      aria-label={copied ? 'Copied!' : 'Copy code to clipboard'}
      title={copied ? 'Copied!' : 'Copy code'}
    >
      {copied ? (
        <span className={styles.copiedIcon}>✓</span>
      ) : (
        <span className={styles.copyIcon}>📋</span>
      )}
    </button>
  );
}
