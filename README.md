# ezpyai

Welcome to `ezpyai`, your new best friend in the wild, wild world of AI! Whether you're a coding wizard, a data sorcerer, or just someone who likes to mess around with powerful tools, this Python utility library is here to make your life easier and your AI dreams a reality. Hack the planet, one prompt at a time!

## Features

- **Easy Integration**: Plug and play with OpenAI's API(and others in the future like LM Studio, Groq, HuggingFace, custom ones, etc). No need to sacrifice any goats.
- **Simplified Prompts**: Wrangle those prompts like a boss. Customize to your heart's content.
- **Structured Responses**: Get clean, validated JSON responses without the hassle. Because who has time for messy data?

## Installation

Getting started is a breeze. Just run this magic spell in your terminal:

```bash
pip install ezpyai
```

Boom! You're ready to rock.

## Usage

Here's a quick primer on how to use `ezpyai`. It's so simple, your pet hamster could do it (assuming it's a really smart hamster).

```python
from ezpyai.llm import OpenAI, Prompt

# Initialize the OpenAI client
ai_client = OpenAI(api_key="your_openai_api_key")

# Create a prompt
prompt = Prompt(user_message="Hello, world!")

# Get a response from the model
response = ai_client.get_response(prompt)
print(response)
```

See? Easy peasy, lemon squeezy.

## Documentation

Want to dive deeper? Check out our [documentation](https://github.com/psyb0t/ezpyai). It's packed with everything you need to become an AI rockstar.

## Contributing

We love contributions like hackers love caffeine. Found a bug? Have a brilliant idea? Head over to the [issues page](https://github.com/psyb0t/ezpyai/issues) and let us know. Pull requests are always welcome!

## License

**ezpyai** is unleashed under the WTFPL (Do What The Fuck You Want To Public License). Copy it, change it, or repurpose it to start your own digital riot.
