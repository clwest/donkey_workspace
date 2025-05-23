class VoiceCodexCommandModule:
    """Utility to parse voice commands for codex interactions."""

    def transcribe(self, audio_input):
        """Placeholder transcription. Assumes `audio_input` is already text."""
        return audio_input

    def parse_command(self, transcript: str) -> dict:
        text = transcript.lower().strip()
        if text.startswith("invoke ritual"):
            return {"action": "invoke_ritual", "argument": text[len("invoke ritual"):].strip()}
        if text.startswith("open codex entry"):
            entry = text.split("open codex entry", 1)[1].strip(" :")
            return {"action": "open_codex_entry", "entry": entry}
        if text.startswith("propose codex mutation"):
            statement = text.split("propose codex mutation", 1)[1].strip(" :")
            return {"action": "propose_codex_mutation", "statement": statement}
        return {"action": "unknown", "raw": transcript}

