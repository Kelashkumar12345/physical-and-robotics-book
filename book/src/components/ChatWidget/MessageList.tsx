import React, { useEffect, useRef } from 'react';
import CitationList from './CitationList';
import type { Message } from './index';
import styles from './styles.module.css';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({
  messages,
  isLoading,
}: MessageListProps): JSX.Element {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className={styles.messageList}>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🤖</div>
          <p>Ask me anything about Physical AI & Robotics!</p>
          <ul className={styles.suggestions}>
            <li>What is ROS 2?</li>
            <li>How does VSLAM work?</li>
            <li>Explain URDF format</li>
            <li>What is Isaac Sim?</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.messageList}>
      {messages.map(message => (
        <div
          key={message.id}
          className={`${styles.message} ${styles[message.role]}`}
        >
          <div className={styles.messageContent}>
            {message.content}
            {message.isOutOfScope && (
              <span className={styles.outOfScope}>
                ℹ️ This topic is outside the book's scope
              </span>
            )}
          </div>
          {message.citations && message.citations.length > 0 && (
            <CitationList citations={message.citations} />
          )}
        </div>
      ))}
      {isLoading && (
        <div className={`${styles.message} ${styles.assistant}`}>
          <div className={styles.loading}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
