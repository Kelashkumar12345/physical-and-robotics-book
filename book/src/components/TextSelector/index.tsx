import React, { useState, useEffect, useCallback } from 'react';
import ContextMenu from './ContextMenu';
import styles from './styles.module.css';

const MAX_SELECTION_LENGTH = 2000;

interface SelectionPosition {
  x: number;
  y: number;
}

export default function TextSelector(): JSX.Element | null {
  const [selectedText, setSelectedText] = useState<string>('');
  const [menuPosition, setMenuPosition] = useState<SelectionPosition | null>(null);
  const [isTruncated, setIsTruncated] = useState(false);

  const handleMouseUp = useCallback((event: MouseEvent) => {
    // Small delay to allow selection to complete
    setTimeout(() => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() || '';

      if (text.length > 10) {
        // Get the selection range position
        const range = selection?.getRangeAt(0);
        if (range) {
          const rect = range.getBoundingClientRect();
          setMenuPosition({
            x: rect.left + rect.width / 2,
            y: rect.top - 10,
          });

          // Check if truncation is needed
          if (text.length > MAX_SELECTION_LENGTH) {
            setSelectedText(text.slice(0, MAX_SELECTION_LENGTH));
            setIsTruncated(true);
          } else {
            setSelectedText(text);
            setIsTruncated(false);
          }
        }
      } else {
        setMenuPosition(null);
        setSelectedText('');
      }
    }, 10);
  }, []);

  const handleMouseDown = useCallback(() => {
    setMenuPosition(null);
    setSelectedText('');
  }, []);

  const handleAskAboutThis = useCallback(() => {
    if (selectedText) {
      // Dispatch custom event to ChatWidget
      const event = new CustomEvent('chatbot-context', {
        detail: { text: selectedText },
      });
      window.dispatchEvent(event);

      // Clear selection
      window.getSelection()?.removeAllRanges();
      setMenuPosition(null);
      setSelectedText('');
    }
  }, [selectedText]);

  const handleClose = useCallback(() => {
    setMenuPosition(null);
    setSelectedText('');
    window.getSelection()?.removeAllRanges();
  }, []);

  useEffect(() => {
    // Only attach to content areas
    const contentArea = document.querySelector('.markdown, article, .theme-doc-markdown');

    if (contentArea) {
      contentArea.addEventListener('mouseup', handleMouseUp as EventListener);
      contentArea.addEventListener('mousedown', handleMouseDown as EventListener);
    }

    return () => {
      if (contentArea) {
        contentArea.removeEventListener('mouseup', handleMouseUp as EventListener);
        contentArea.removeEventListener('mousedown', handleMouseDown as EventListener);
      }
    };
  }, [handleMouseUp, handleMouseDown]);

  // Handle keyboard escape
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && menuPosition) {
        handleClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [menuPosition, handleClose]);

  if (!menuPosition) {
    return null;
  }

  return (
    <ContextMenu
      position={menuPosition}
      onAskAboutThis={handleAskAboutThis}
      onClose={handleClose}
      isTruncated={isTruncated}
    />
  );
}
