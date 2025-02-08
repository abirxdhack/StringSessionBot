# Telegram Session String Generator Bot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Telethon](https://img.shields.io/badge/Telethon-1.21.1-blue)
![Pyrogram](https://img.shields.io/badge/Pyrogram-1.4.16-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub stars](https://img.shields.io/github/stars/abirxdhack/StringSessionBot)
![GitHub forks](https://img.shields.io/github/forks/abirxdhack/StringSessionBot)

Welcome to the Telegram Session String Generator Bot! This bot helps you generate session strings for both Pyrogram and Telethon clients securely and easily. 🚀

## Features ✨

- Safe and secure session string generation.
- Supports both PyroGram and Telethon clients.
- User-friendly interface.
- Stores nothing, ensuring your privacy.

## Setup Instructions 🛠️

Follow these steps to set up and run the bot:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/abirxdhack/StringSessionBot.git
    cd StringSessionBot
    ```

2. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `config.py` file:**

    ```python
    # config.py
    API_ID = 'your_api_id_here'
    API_HASH = 'your_api_hash_here'
    BOT_TOKEN = 'your_bot_token_here'
    ```

4. **Run the bot:**

    ```bash
    python3 main.py
    ```

## Configuration

1. Open the `config.py` file in your favorite text editor.
2. Replace the placeholders for `API_ID`, `API_HASH`, `BOT_TOKEN`, and with your actual values:
   - **`API_ID`**: Your API ID from [my.telegram.org](https://my.telegram.org).
   - **`API_HASH`**: Your API Hash from [my.telegram.org](https://my.telegram.org).
   - **`BOT_TOKEN`**: The token you obtained from [@BotFather](https://t.me/BotFather).

## Deploy the Bot

```sh
git clone https://github.com/abirxdhack/StringSessionBot
cd StringSessionBot
python main.py
```

## Usage 🚀

- Start a private chat with the bot.
- Use `/start` to get an overview and instructions.
- Use `/pyro` to generate a Pyrogram session string.
- Use `/tele` to generate a Telethon session string.
- Follow the prompts to enter your API ID, API Hash, and phone number.
- Enter the OTP and 2FA (if applicable) to get your session string.

## Example Commands 📋

- `/start` - Get an overview and instructions.
- `/pyro` - Generate a Pyrogram session string.
- `/tele` - Generate a Telethon session string.

## Contributing 🤝

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.



## Contact 📬

For any questions or suggestions, feel free to reach out:

- Telegram: [My Dev👨‍💻](https://t.me/abirxdhack)

