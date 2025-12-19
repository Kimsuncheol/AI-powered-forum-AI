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


# Rewrite templates for different modes

REWRITE_CLARITY_TEMPLATE = """You are a helpful writing assistant that improves text clarity.

Rewrite the following text to make it clearer and easier to understand:
- Fix confusing sentence structures
- Replace jargon with simpler terms where appropriate
- Improve logical flow
- Keep the same meaning and tone

Original text:
{text}

Rewritten text:"""


REWRITE_SHORTEN_TEMPLATE = """You are a helpful writing assistant that makes text more concise.

Rewrite the following text to be shorter while preserving the key information:
- Remove redundant information
- Use concise language
- Keep only essential points
- Maintain the original meaning

Original text:
{text}

Shortened text:"""


REWRITE_POLITE_TEMPLATE = """You are a helpful writing assistant that makes text more polite and professional.

Rewrite the following text to make it more polite and courteous:
- Use respectful language
- Soften harsh or direct statements
- Add appropriate pleasantries
- Maintain professionalism
- Keep the core message intact

Original text:
{text}

Polite text:"""


REWRITE_TRANSLATE_TEMPLATE = """You are a helpful translation assistant.

Translate the following text to {target_language}:
- Preserve the original meaning
- Use natural, idiomatic expressions
- Match the formality level of the original
- Keep technical terms accurate

Original text:
{text}

Translated text:"""


# Additional templates for future AI features

MODERATION_TEMPLATE = """You are a content moderation assistant for a forum.

Analyze the following content for potential policy violations or concerning content.
Consider the following categories:
- spam: Repetitive or promotional content
- harassment: Personal attacks or bullying
- hate_speech: Discriminatory or hateful language
- explicit: Inappropriate or adult content
- violence: Threatening or violent content
- misinformation: Clearly false or misleading claims
- off_topic: Completely unrelated to forum purpose

Respond with a JSON object with this exact structure:
{{
  "risk_score": <float between 0.0 and 1.0>,
  "reason_tags": [<list of applicable categories>],
  "explanation": "<brief explanation of the assessment>"
}}

Content to analyze:
{content}

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
