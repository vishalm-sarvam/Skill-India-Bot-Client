# Skill India - Samvaad Conversational AI Client

A comprehensive Python client for interacting with Sarvam's Samvaad conversational AI agents, built specifically for Skill India applications.

## 🌟 Features

- **🗣️ Multi-language Support**: Conversations in 11 Indian languages (Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Odia, English)
- **🎤 Voice Conversations**: Real-time audio streaming via WebSocket
- **🔧 Custom Tools**: Extend agent capabilities with custom tools
- **📊 Agent Variables**: Maintain conversation context and state
- **🌐 Language Switching**: Dynamically change languages during conversation
- **⚡ Async/Await**: Built on asyncio for efficient concurrent operations

## 📋 Prerequisites

- Python 3.9 or higher
- Samvaad API key (set in `.env`)
- Agent ID (set in `.env`)

For microphone support:
- **macOS**: `brew install portaudio`
- **Ubuntu/Debian**: `sudo apt-get install portaudio19-dev`
- **Windows**: Download from [portaudio.com](http://www.portaudio.com/)

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
uv pip install -e .
```

### 2. Configuration

Create a `.env` file with your Samvaad credentials:

```env
SAMVAAD_API_KEY=<your-samvaad-api-key>
SIA_AGENT_ID=<your-agent-id>
```

### 3. Run

```bash
# Run the agent (uses virtual environment)
.venv/bin/python main.py
```

The agent will:
- Connect to Samvaad
- Start listening/responding
- Run until you press Ctrl+C

## 📚 Usage

The `main.py` script connects to the Samvaad agent and runs until interrupted:

```python
# Just run it
.venv/bin/python main.py
```

To customize, edit `main.py` or use the client directly:

```python
import asyncio
from samvaad_client import SamvaadClient

async def main():
    client = SamvaadClient(
        user_id="your_user_id",
        initial_language="English",  # or Hindi, Tamil, etc.
    )

    def on_text(text: str):
        print(f"Agent: {text}")

    client.set_text_callback(on_text)

    await client.start()
    await client.wait_for_disconnect()
    await client.stop()

asyncio.run(main())
```

## 🏗️ Project Structure

```
Skill-India-Demo/
├── samvaad_client.py          # Main client implementation
├── main.py                     # Simple agent runner
├── .env                        # API credentials
├── pyproject.toml             # Project dependencies
└── README.md                   # This file
```


## 📖 API Reference

### SamvaadClient

Main client class for Samvaad agent interaction.

**Parameters:**
- `api_key` (str, optional): API key (defaults to `SAMVAAD_API_KEY` env var)
- `agent_id` (str, optional): Agent ID (defaults to `SIA_AGENT_ID` env var)
- `user_id` (str): User identifier
- `org_id` (str): Organization ID (default: "org_ai")
- `workspace_id` (str, optional): Workspace ID (defaults to agent_id)
- `sample_rate` (int): Audio sample rate - 8000 or 16000 Hz (default: 16000)
- `initial_language` (str, optional): Starting language
- `agent_variables` (dict, optional): Initial agent variables

**Methods:**
- `async start()`: Connect to agent
- `async stop()`: Disconnect and cleanup
- `async send_audio(audio_data: bytes)`: Send raw audio
- `async send_audio_file(file_path: str)`: Send audio from file
- `async wait_for_disconnect()`: Wait until disconnected
- `is_connected() -> bool`: Check connection status
- `set_text_callback(callback)`: Set text response handler
- `set_audio_callback(callback)`: Set audio response handler
- `set_event_callback(callback)`: Set event handler

### SamvaadClientWithMicrophone

Extended client with microphone support (requires PyAudio).

**Additional Methods:**
- `async start_microphone_conversation(chunk_size: int)`: Start voice conversation

## 🌍 Supported Languages

The client supports conversations in:

1. **English**
2. **Hindi** (हिंदी)
3. **Bengali** (বাংলা)
4. **Tamil** (தமிழ்)
5. **Telugu** (తెలుగు)
6. **Gujarati** (ગુજરાતી)
7. **Kannada** (ಕನ್ನಡ)
8. **Malayalam** (മലയാളം)
9. **Marathi** (मराठी)
10. **Punjabi** (ਪੰਜਾਬੀ)
11. **Odia** (ଓଡ଼ିଆ)

## 🛠️ Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

## 🎯 Use Cases

This client is ideal for:

- **Skill India Program**: Course information and registration assistance
- **Multilingual Customer Support**: Voice and text support in Indian languages
- **Educational Platforms**: Interactive learning assistants
- **Government Services**: Citizen engagement and information dissemination
- **Voice-based Applications**: IVR systems, voice bots, audio processing

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SAMVAAD_API_KEY` | Samvaad API authentication key | Yes |
| `SIA_AGENT_ID` | Agent/App ID for Skill India agent | Yes |

## 🔒 Security Notes

- Never commit `.env` file to version control
- Store API keys securely
- Use environment-specific credentials
- Implement proper error handling for production use

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Refer to [Sarvam SDK documentation](https://agent-docs.azurewebsites.net/sdks/python)
- Contact Skill India support

## 🙏 Acknowledgments

- Built with [Sarvam Conversational AI SDK](https://sarvam.ai/)
- Developed for Skill India initiative

---

Made with ❤️ for Digital India
