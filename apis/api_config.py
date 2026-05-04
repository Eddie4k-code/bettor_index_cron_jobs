import os

class APIConfig:
	"""
	Holds configuration for external API access, such as API keys and base URLs.
	"""
	def __init__(self, api_key_env_var, base_url=None):
		self.api_key = os.getenv(api_key_env_var)
		self.base_url = base_url
		if not self.api_key:
			raise ValueError(f"API key not found in environment variable: {api_key_env_var}")

	def get_api_key(self):
		return self.api_key

	def get_base_url(self):
		return self.base_url
    