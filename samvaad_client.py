"""
Samvaad Conversational AI Client

A Python client for interacting with Sarvam's Samvaad conversational AI agents.
Supports real-time voice conversations, multi-language support, and custom tools.
"""

import asyncio
import os
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr
from sarvam_conv_ai_sdk import (
    AsyncSamvaadAgent,
    AsyncDefaultAudioInterface,
    InteractionConfig,
    InteractionType,
)
from sarvam_conv_ai_sdk.messages.types import UserIdentifierType


class SamvaadClient:
    """
    High-level client for Samvaad conversational AI agent.

    Features:
    - Automatic credential loading from .env
    - Callback support for text, audio, and events
    - Simple async interface
    - Language switching
    - Agent variable management
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: str = "demo_user",
        org_id: str = "nsdcindia.org",
        workspace_id: str = "nsdcindia-org-defa-68af9a",
        sample_rate: int = 16000,
        initial_language: Optional[str] = None,
        agent_variables: Optional[Dict[str, Any]] = None,
        enable_audio: bool = False,
    ):
        """
        Initialize Samvaad client.

        Args:
            api_key: Samvaad API key (loads from SAMVAAD_API_KEY env var if not provided)
            agent_id: Agent ID (loads from SIA_AGENT_ID env var if not provided)
            user_id: User identifier for the conversation
            org_id: Organization ID (default: nsdcindia.org)
            workspace_id: Workspace ID (default: nsdcindia-org-defa-68af9a)
            sample_rate: Audio sample rate (8000 or 16000 Hz)
            initial_language: Starting language (e.g., 'Hindi', 'English')
            agent_variables: Initial agent variables dict
            enable_audio: Enable audio playback through speakers (requires PyAudio)
        """
        # Load environment variables
        load_dotenv()

        self.api_key = api_key or os.getenv("SAMVAAD_API_KEY")
        self.agent_id = agent_id or os.getenv("SIA_AGENT_ID")

        if not self.api_key:
            raise ValueError("API key not provided. Set SAMVAAD_API_KEY env var or pass api_key parameter")

        if not self.agent_id:
            raise ValueError("Agent ID not provided. Set SIA_AGENT_ID env var or pass agent_id parameter")

        self.workspace_id = workspace_id
        self.org_id = org_id
        self.enable_audio = enable_audio
        self.sample_rate = sample_rate

        # Create interaction config
        self.config = InteractionConfig(
            user_identifier_type=UserIdentifierType.CUSTOM,
            user_identifier=user_id,
            org_id=self.org_id,
            workspace_id=self.workspace_id,
            app_id=self.agent_id,
            interaction_type=InteractionType.CALL,
            sample_rate=sample_rate,
            initial_language_name=initial_language,
            agent_variables=agent_variables or {},
        )

        # Initialize agent (will be created in start())
        self.agent: Optional[AsyncSamvaadAgent] = None

        # Callback handlers
        self.on_text_callback: Optional[Callable[[str], None]] = None
        self.on_audio_callback: Optional[Callable[[bytes], None]] = None
        self.on_event_callback: Optional[Callable[[Dict], None]] = None

    def set_text_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for receiving text responses from agent."""
        self.on_text_callback = callback

    def set_audio_callback(self, callback: Callable[[bytes], None]) -> None:
        """Set callback for receiving audio responses from agent."""
        self.on_audio_callback = callback

    def set_event_callback(self, callback: Callable[[Dict], None]) -> None:
        """Set callback for receiving event notifications."""
        self.on_event_callback = callback

    async def start(self) -> None:
        """
        Start the agent and establish WebSocket connection.

        Raises:
            Exception: If connection fails
        """
        # Create async wrappers for callbacks
        async def text_callback(msg):
            if self.on_text_callback:
                text = msg.text if hasattr(msg, 'text') else str(msg)
                self.on_text_callback(text)

        async def audio_callback(msg):
            if self.on_audio_callback:
                audio_data = msg.audio if hasattr(msg, 'audio') else b''
                self.on_audio_callback(audio_data)

        async def event_callback(event):
            if self.on_event_callback:
                event_dict = event.model_dump() if hasattr(event, 'model_dump') else {'type': str(event)}
                self.on_event_callback(event_dict)

        # Set up audio interface if enabled
        audio_interface = None
        if self.enable_audio:
            try:
                audio_interface = AsyncDefaultAudioInterface(input_sample_rate=self.sample_rate)
                print(f"✓ Audio playback enabled ({self.sample_rate} Hz)")
            except Exception as e:
                print(f"⚠ Audio playback unavailable: {e}")
                print("  Install: brew install portaudio && uv pip install pyaudio")

        self.agent = AsyncSamvaadAgent(
            api_key=SecretStr(self.api_key),
            config=self.config,
            audio_interface=audio_interface,
            text_callback=text_callback if self.on_text_callback else None,
            audio_callback=audio_callback if self.on_audio_callback else None,
            event_callback=event_callback if self.on_event_callback else None,
        )

        await self.agent.start()
        print(f"✓ Connected to Samvaad agent: {self.agent_id}")

    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        if self.agent:
            await self.agent.stop()
            print("✓ Disconnected from Samvaad agent")

    async def send_audio(self, audio_data: bytes) -> None:
        """
        Send raw audio data to the agent.

        Args:
            audio_data: Raw PCM audio bytes (16-bit mono, matching sample_rate)

        Raises:
            RuntimeError: If agent not started
        """
        if not self.agent:
            raise RuntimeError("Agent not started. Call start() first.")

        await self.agent.send_audio(audio_data)

    async def send_audio_file(self, file_path: str) -> None:
        """
        Send audio from a file to the agent.

        Args:
            file_path: Path to audio file (must be 16-bit PCM mono WAV)

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If agent not started
        """
        if not self.agent:
            raise RuntimeError("Agent not started. Call start() first.")

        audio_path = Path(file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        with open(audio_path, "rb") as f:
            # Skip WAV header (44 bytes) if it's a WAV file
            if file_path.lower().endswith('.wav'):
                f.seek(44)
            audio_data = f.read()

        await self.agent.send_audio(audio_data)
        print(f"✓ Sent audio from {file_path}")

    async def wait_for_disconnect(self) -> None:
        """Wait until the agent disconnects."""
        if self.agent:
            await self.agent.wait_for_disconnect()

    def is_connected(self) -> bool:
        """Check if agent is currently connected."""
        return self.agent is not None and self.agent.is_connected()

    async def run_conversation(self, duration: Optional[float] = None) -> None:
        """
        Run a conversation session.

        Args:
            duration: Optional timeout in seconds. If None, runs until disconnect.
        """
        await self.start()

        try:
            if duration:
                await asyncio.sleep(duration)
            else:
                await self.wait_for_disconnect()
        finally:
            await self.stop()


class SamvaadClientWithMicrophone(SamvaadClient):
    """
    Extended client with microphone input support.
    Requires portaudio system dependency.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import pyaudio
            self.pyaudio = pyaudio
        except ImportError:
            raise ImportError(
                "PyAudio not installed. Install with: pip install sarvam-conv-ai-sdk[all]\n"
                "Also ensure portaudio is installed on your system."
            )

    async def start_microphone_conversation(self, chunk_size: int = 1024) -> None:
        """
        Start a conversation using microphone input.

        Args:
            chunk_size: Audio chunk size in samples
        """
        await self.start()

        # Initialize PyAudio
        p = self.pyaudio.PyAudio()

        # Open microphone stream
        stream = p.open(
            format=self.pyaudio.paInt16,
            channels=1,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=chunk_size,
        )

        print("🎤 Microphone active. Speak to the agent. Press Ctrl+C to stop.")

        try:
            while self.is_connected():
                audio_chunk = stream.read(chunk_size, exception_on_overflow=False)
                await self.send_audio(audio_chunk)
        except KeyboardInterrupt:
            print("\n✓ Stopping conversation...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            await self.stop()


# Example usage and demos
async def demo_basic_conversation():
    """Basic demo: Connect and wait for disconnect."""
    print("=== Basic Samvaad Conversation Demo ===\n")

    client = SamvaadClient(
        user_id="demo_user_001",
        initial_language="English",
    )

    # Set up callbacks
    def on_text(text: str):
        print(f"Agent: {text}")

    def on_event(event: Dict):
        print(f"Event: {event.get('type', 'unknown')}")

    client.set_text_callback(on_text)
    client.set_event_callback(on_event)

    # Run conversation
    await client.run_conversation(duration=30)  # 30 second demo


async def demo_with_audio_file():
    """Demo: Send audio file to agent."""
    print("=== Audio File Demo ===\n")

    client = SamvaadClient(user_id="demo_user_002")

    def on_text(text: str):
        print(f"Agent response: {text}")

    client.set_text_callback(on_text)

    await client.start()

    # Send audio file (create your own audio file)
    # await client.send_audio_file("path/to/your/audio.wav")

    await asyncio.sleep(10)  # Wait for response
    await client.stop()


async def demo_with_variables():
    """Demo: Using agent variables."""
    print("=== Agent Variables Demo ===\n")

    client = SamvaadClient(
        user_id="demo_user_003",
        agent_variables={
            "user_name": "Vishal",
            "language_preference": "Hindi",
            "topic": "Skill India Program",
        }
    )

    def on_text(text: str):
        print(f"Agent: {text}")

    client.set_text_callback(on_text)

    await client.run_conversation(duration=20)


async def main():
    """Main entry point for demos."""
    print("Samvaad Client Demo\n")
    print("Choose a demo:")
    print("1. Basic conversation (30 seconds)")
    print("2. Audio file upload")
    print("3. Agent variables demo")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        await demo_basic_conversation()
    elif choice == "2":
        await demo_with_audio_file()
    elif choice == "3":
        await demo_with_variables()
    else:
        print("Invalid choice. Running basic demo...")
        await demo_basic_conversation()


if __name__ == "__main__":
    asyncio.run(main())
