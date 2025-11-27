from dotenv import load_dotenv
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 1. Load Environment Variables
load_dotenv()

class LLMRouter:
    """
    A resilient router that handles retries, backoffs, and model fallbacks.
    """

    def __init__(self):
        # Configuration: Model Names

        # 1. PRIMARY: Keep this BROKEN (to force the error)
        self.primary_model = "gemini/gemini-2.0-flash"

        # 2. BACKUP: Use this VALID model (Llama 3 via Groq)
        # This guarantees you get an answer when the primary fails.
        self.backup_model = "groq/llama-3.1-8b-instant"


    def _call_llm(self, model_name, messages, **kwargs):
        """
        A private helper function to make the actual API call.
        """
        print(f"   ...Attempting to call: {model_name}")
        return completion(
            model=model_name,
            messages=messages,
            **kwargs  # Pass through temperature, max_tokens, etc.
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _execute_primary_with_retry(self, messages, **kwargs):
        return self._call_llm(self.primary_model, messages, **kwargs)

    def generate_response(self, prompt, **kwargs):
        """
        The Main Public Method.
        Tries Primary Model -> Retries -> Falls back to Backup Model.
        """
        messages = [{"role": "user", "content": prompt}]

        try:
            # Step 1: Try Primary
            print(f"⚡ Requesting Primary Model: {self.primary_model}")
            response = self._execute_primary_with_retry(messages, **kwargs)

            # Check for "Silent Failure" (Content is None)
            content = response['choices'][0]['message']['content']
            if content is None:
                raise ValueError("Primary model returned empty content.")

            return {
                "content": content,
                "model_used": self.primary_model,
                "status": "success"
            }

        except Exception as e:
            # Step 2: Primary Failed. Switch to Backup.
            print(f"PRIMARY FAILED. Switching to Fallback: {self.backup_model}")
            print(f"   Error log: {str(e)}")

            try:
                # Step 3: Try Backup
                response = self._call_llm(self.backup_model, messages, **kwargs)
                content = response['choices'][0]['message']['content']

                # Check for "Silent Failure" in Backup too
                if content is None:
                    # If Gemini blocks it, we need to see why.
                    # Usually it's safety settings, so we return a helpful message.
                    content = "The Backup Model blocked the response (Safety Filters or Empty Return)."

                return {
                    "content": content,
                    "model_used": self.backup_model,
                    "status": "fallback_success"
                }
            except Exception as backup_error:
                # Step 4: Total System Failure
                return {
                    "content": f"System Error: Both models failed. {str(backup_error)}",
                    "model_used": "None",
                    "status": "failure"
                }