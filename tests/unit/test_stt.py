"""Unit tests for STT (Speech-to-Text) functionality."""

from app.infrastructure.stt.whisper_client import (
    SUPPORTED_AUDIO_FORMATS,
    is_audio_file,
)


class TestIsAudioFile:
    """Tests for is_audio_file function."""

    def test_mp3_is_audio(self):
        assert is_audio_file("recording.mp3") is True

    def test_wav_is_audio(self):
        assert is_audio_file("recording.wav") is True

    def test_m4a_is_audio(self):
        assert is_audio_file("recording.m4a") is True

    def test_mp4_is_audio(self):
        assert is_audio_file("video.mp4") is True

    def test_webm_is_audio(self):
        assert is_audio_file("recording.webm") is True

    def test_ogg_is_audio(self):
        assert is_audio_file("audio.ogg") is True

    def test_txt_is_not_audio(self):
        assert is_audio_file("conversation.txt") is False

    def test_json_is_not_audio(self):
        assert is_audio_file("data.json") is False

    def test_csv_is_not_audio(self):
        assert is_audio_file("data.csv") is False

    def test_uppercase_extension(self):
        assert is_audio_file("recording.MP3") is True

    def test_mixed_case_extension(self):
        assert is_audio_file("recording.Mp3") is True

    def test_no_extension(self):
        assert is_audio_file("noextension") is False

    def test_empty_filename(self):
        assert is_audio_file("") is False


class TestSupportedAudioFormats:
    """Tests for supported audio formats constant."""

    def test_mp3_supported(self):
        assert "mp3" in SUPPORTED_AUDIO_FORMATS

    def test_wav_supported(self):
        assert "wav" in SUPPORTED_AUDIO_FORMATS

    def test_m4a_supported(self):
        assert "m4a" in SUPPORTED_AUDIO_FORMATS

    def test_mp4_supported(self):
        assert "mp4" in SUPPORTED_AUDIO_FORMATS

    def test_webm_supported(self):
        assert "webm" in SUPPORTED_AUDIO_FORMATS

    def test_ogg_supported(self):
        assert "ogg" in SUPPORTED_AUDIO_FORMATS
