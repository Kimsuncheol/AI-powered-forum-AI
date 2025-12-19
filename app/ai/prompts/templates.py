"""Prompt templates for AI chains."""

SUMMARIZER_TEMPLATE = """You are a helpful assistant that summarizes forum discussions.

Given the following forum thread content, provide a concise summary that captures:
1. The main topic or question
2. Key points discussed
3. Any conclusions or resolutions

Thread Content:
{thread_content}

Summary:"""


QA_TEMPLATE = """You are a helpful assistant that answers questions based on forum discussions.

Use only the information provided in the context to answer the question.
If the answer cannot be found in the context, say "I couldn't find relevant information in the discussion."

Context:
{context}

Question: {question}

Answer:"""


# Additional templates for future AI features

MODERATION_TEMPLATE = """You are a content moderator for a forum.

Analyze the following content and determine if it violates community guidelines.
Consider: spam, harassment, hate speech, inappropriate content, or off-topic posts.

Content:
{content}

Respond with a JSON object:
{{"is_appropriate": true/false, "reason": "explanation if inappropriate", "confidence": 0.0-1.0}}

Analysis:"""


SUGGESTION_TEMPLATE = """You are a helpful assistant that suggests improvements to forum posts.

Given the following draft post, suggest improvements for:
1. Clarity
2. Grammar and spelling
3. Formatting
4. Completeness

Draft:
{draft}

Suggestions:"""
