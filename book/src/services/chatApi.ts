/**
 * Chat API client for the RAG chatbot backend.
 */

export interface ChatRequest {
  message: string;
  context?: string;
}

export interface Citation {
  title: string;
  url: string;
  relevanceScore?: number;
}

export interface ChatResponse {
  id: string;
  message: string;
  citations: Citation[];
  isOutOfScope: boolean;
  questionsRemaining: number;
}

export interface SessionStatus {
  sessionId: string;
  questionCount: number;
  questionsRemaining: number;
  hasContext: boolean;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

class ChatApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    // Default to localhost for development, can be overridden via constructor
    this.baseUrl = baseUrl || 'http://localhost:8000';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'unknown',
        message: `HTTP error ${response.status}`,
      }));
      throw new ChatApiError(response.status, error);
    }

    return response.json();
  }

  /**
   * Send a message to the chatbot.
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get current session status.
   */
  async getSessionStatus(): Promise<SessionStatus> {
    return this.request<SessionStatus>('/api/v1/chat/session');
  }

  /**
   * Reset the current session.
   */
  async resetSession(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/v1/chat/session', {
      method: 'DELETE',
    });
  }

  /**
   * Check API health.
   */
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    dependencies: { qdrant: string; openai: string };
  }> {
    return this.request('/api/v1/health');
  }
}

export class ChatApiError extends Error {
  public readonly status: number;
  public readonly error: ApiError;

  constructor(status: number, error: ApiError) {
    super(error.message);
    this.name = 'ChatApiError';
    this.status = status;
    this.error = error;
  }

  get isRateLimited(): boolean {
    return this.status === 429;
  }

  get isServiceUnavailable(): boolean {
    return this.status === 503;
  }
}

// Export singleton instance
export const chatApi = new ChatApiClient();

export default chatApi;
