import React, { useState, useCallback } from 'react';
import ChatWindow from './ChatWindow';
import styles from './styles.module.css';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  isOutOfScope?: boolean;
}

export interface Citation {
  title: string;
  url: string;
  relevanceScore?: number;
}

export interface ChatWidgetProps {
  apiUrl?: string;
}

export default function ChatWidget({ apiUrl }: ChatWidgetProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [questionsRemaining, setQuestionsRemaining] = useState(50);
  const [selectedContext, setSelectedContext] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Use Vercel API in production, localhost for development
  const baseUrl = apiUrl || 'https://api-five-sepia-88.vercel.app';

  const toggleOpen = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const clearContext = useCallback(() => {
    setSelectedContext(null);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: content.trim(),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await fetch(`${baseUrl}/api/v1/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            message: content.trim(),
            context: selectedContext,
          }),
        });

        if (!response.ok) {
          if (response.status === 429) {
            setError('You have reached the 50 question limit. Please start a new session.');
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return;
        }

        const data = await response.json();

        const assistantMessage: Message = {
          id: data.id,
          role: 'assistant',
          content: data.message,
          citations: data.citations,
          isOutOfScope: data.isOutOfScope,
        };

        setMessages(prev => [...prev, assistantMessage]);
        setQuestionsRemaining(data.questionsRemaining);
        setSelectedContext(null);
      } catch (err) {
        setError('Unable to connect to the chatbot. Please try again later.');
        console.error('Chat error:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [baseUrl, isLoading, selectedContext]
  );

  const resetSession = useCallback(async () => {
    try {
      await fetch(`${baseUrl}/api/v1/chat/session`, {
        method: 'DELETE',
        credentials: 'include',
      });
      setMessages([]);
      setQuestionsRemaining(50);
      setError(null);
    } catch (err) {
      console.error('Reset error:', err);
    }
  }, [baseUrl]);

  // Listen for text selection events from TextSelector
  React.useEffect(() => {
    const handleTextSelection = (event: CustomEvent<{ text: string }>) => {
      setSelectedContext(event.detail.text);
      setIsOpen(true);
    };

    window.addEventListener('chatbot-context' as any, handleTextSelection);
    return () => {
      window.removeEventListener('chatbot-context' as any, handleTextSelection);
    };
  }, []);

  return (
    <div className={styles.container}>
      {isOpen && (
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          questionsRemaining={questionsRemaining}
          selectedContext={selectedContext}
          error={error}
          onSend={sendMessage}
          onClose={toggleOpen}
          onReset={resetSession}
          onClearContext={clearContext}
        />
      )}
      <button
        className={styles.toggleButton}
        onClick={toggleOpen}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? '✕' : '💬'}
      </button>
    </div>
  );
}
