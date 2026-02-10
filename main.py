"""
Skill India Demo - Samvaad Conversational AI Client

Simple agent runner - just connects and runs.
"""

import asyncio
from samvaad_client import SamvaadClient


async def main():
    """Run the Samvaad agent."""

    # Create client with audio enabled
    client = SamvaadClient(
        enable_audio=True,  # Enable audio playback
    )

    # Set up callbacks
    def on_text(text: str):
        print(f"\nAgent: {text}")

    def on_audio(_audio_bytes: bytes):
        # Receive audio but don't process it (prevents warning spam)
        pass

    def on_event(event: dict):
        event_type = event.get("type", "unknown")
        # Only show important events
        if event_type in ["conversation_started", "conversation_ended", "error"]:
            print(f"[Event: {event_type}]")

    client.set_text_callback(on_text)
    client.set_audio_callback(on_audio)
    client.set_event_callback(on_event)

    # Start conversation
    try:
        print("Connecting to Samvaad...")
        await client.start()
        print("✓ Connected! Press Ctrl+C to stop.\n")

        # Wait for disconnect
        await client.wait_for_disconnect()

    except KeyboardInterrupt:
        print("\n\n[Stopping...]")
    except Exception as e:
        print(f"\n[Error: {e}]")
    finally:
        await client.stop()
        print("✓ Disconnected.\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C
