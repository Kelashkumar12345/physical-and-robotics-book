"""OpenAI Agents SDK integration for conversational AI."""

from openai import AsyncOpenAI


class AgentService:
    """Service for conversational AI using OpenAI."""

    MODEL = "gpt-4-turbo-preview"
    SYSTEM_PROMPT = """You are a helpful assistant for the Physical AI & Humanoid Robotics Book.
Your role is to answer questions about the book content, including:
- ROS 2 (Robot Operating System 2) fundamentals
- Gazebo and Unity simulation
- NVIDIA Isaac SDK and Isaac Sim
- VLA (Vision-Language-Action) models
- Humanoid robotics and locomotion

Guidelines:
1. Answer based on the provided context from the book
2. If the question is outside the book's scope, politely indicate this
3. Cite specific sections when relevant
4. Provide code examples when helpful
5. Explain complex concepts in accessible terms

If you cannot find relevant information in the provided context, say so clearly."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def chat(
        self,
        message: str,
        context: str | None = None,
        retrieved_chunks: list[dict] | None = None,
        conversation_history: list[dict] | None = None,
    ) -> tuple[str, bool]:
        """
        Generate a response to a user message.

        Returns:
            Tuple of (response_text, is_out_of_scope)
        """
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add retrieved context
        if retrieved_chunks:
            context_text = "\n\n".join(
                f"[Source: {chunk['payload'].get('url', 'unknown')}]\n{chunk['payload'].get('content', '')}"
                for chunk in retrieved_chunks
            )
            messages.append({
                "role": "system",
                "content": f"Relevant book content:\n\n{context_text}",
            })

        # Add user-selected context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"User selected this text for context:\n\n{context}",
            })

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        response = await self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        response_text = response.choices[0].message.content or ""

        # Simple out-of-scope detection
        is_out_of_scope = (
            "outside the scope" in response_text.lower()
            or "not covered in the book" in response_text.lower()
            or "i don't have information" in response_text.lower()
        )

        return response_text, is_out_of_scope
