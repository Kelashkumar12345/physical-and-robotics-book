import React from 'react';
import styles from './styles.module.css';

interface ContextMenuProps {
  position: { x: number; y: number };
  onAskAboutThis: () => void;
  onClose: () => void;
  isTruncated: boolean;
}

export default function ContextMenu({
  position,
  onAskAboutThis,
  onClose,
  isTruncated,
}: ContextMenuProps): JSX.Element {
  return (
    <div
      className={styles.contextMenu}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <button
        onClick={onAskAboutThis}
        className={styles.menuButton}
        title="Ask the chatbot about this selection"
      >
        💬 Ask about this
      </button>
      {isTruncated && (
        <span className={styles.truncationNotice}>
          (Text will be truncated to 2000 chars)
        </span>
      )}
    </div>
  );
}
