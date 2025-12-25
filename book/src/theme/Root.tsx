import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';
import TextSelector from '@site/src/components/TextSelector';

interface RootProps {
  children: React.ReactNode;
}

// Theme wrapper that injects ChatWidget and TextSelector globally
export default function Root({ children }: RootProps): JSX.Element {
  return (
    <>
      {children}
      <ChatWidget />
      <TextSelector />
    </>
  );
}
