from groq import Groq
from config import Config

class ContentGenerator:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        # Using Llama 3.3 70B for high-quality content
        self.model_id = 'llama-3.3-70b-versatile'

    def generate_post(self, data):
        """Generates platform-specific social media content using Groq."""
        prompt = self._build_prompt(data)
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_id,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content via Groq: {e}")
            return None

    def _build_prompt(self, data):
        platform = data['platform']
        tone = data['tone']
        topic = data['topic']
        audience = data.get('audience', 'general audience')
        keywords = data.get('keywords', '')
        cta = data.get('cta', '')

        system_instruction = f"""
        You are an expert social media manager. Generate a {platform} post about '{topic}'.
        Tone: {tone}
        Target Audience: {audience}
        Keywords/Hashtags: {keywords}
        Call to Action: {cta}

        Rules:
        - Adapt writing style strictly for {platform}.
        - LinkedIn: Professional, value-driven, insights/advice, 3-5 hashtags, use line breaks.
        - Twitter/X: Concise, punchy, strong hook, 1-3 hashtags.
        - Instagram: Conversational, storytelling, emojis allowed, up to 10 hashtags.
        - Facebook: Friendly, community-focused, encourage discussion.
        - Avoid emojis unless it's Instagram or Facebook.
        - Stay within character limits for the platform.
        - Return ONLY the final post text. No markdown unless the platform supports it.
        """
        return system_instruction
