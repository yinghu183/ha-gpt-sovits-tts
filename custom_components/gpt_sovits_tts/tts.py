"""Support for the GPT-SoVITS TTS service."""
import logging
import asyncio
from http import HTTPStatus
from typing import Any
from urllib.parse import urlencode

import aiohttp
import voluptuous as vol

from homeassistant.components.tts import (
    PLATFORM_SCHEMA,
    Provider,
    TtsAudioType,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# --- Configuration Constants ---
CONF_REFER_WAV_PATH = "refer_wav_path"
CONF_PROMPT_TEXT = "prompt_text"
CONF_PROMPT_LANGUAGE = "prompt_language"
CONF_TEXT_LANGUAGE = "text_language"
CONF_TOP_K = "top_k"
CONF_TOP_P = "top_p"
CONF_TEMPERATURE = "temperature"
CONF_SPEED = "speed"

# --- Default Values ---
DEFAULT_PORT = 9880
DEFAULT_PROMPT_LANGUAGE = "zh"
DEFAULT_TEXT_LANGUAGE = "zh"
DEFAULT_TOP_K = 15
DEFAULT_TOP_P = 1.0
DEFAULT_TEMPERATURE = 1.0
DEFAULT_SPEED = 1.0

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_REFER_WAV_PATH): cv.string,
        vol.Required(CONF_PROMPT_TEXT): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_PROMPT_LANGUAGE, default=DEFAULT_PROMPT_LANGUAGE): cv.string,
        vol.Optional(CONF_TEXT_LANGUAGE, default=DEFAULT_TEXT_LANGUAGE): cv.string,
        vol.Optional(CONF_TOP_K, default=DEFAULT_TOP_K): cv.positive_int,
        vol.Optional(CONF_TOP_P, default=DEFAULT_TOP_P): vol.Coerce(float),
        vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.Coerce(float),
        vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): vol.Coerce(float),
    }
)

async def async_get_engine(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> Provider:
    """Set up GPT-SoVITS TTS component."""
    return GptSovitsProvider(hass, config)


class GptSovitsProvider(Provider):
    """The GPT-SoVITS TTS provider."""

    def __init__(self, hass: HomeAssistant, config: ConfigType) -> None:
        """Initialize the provider."""
        self.hass = hass
        self._name = "GPT-SoVITS"
        self._config = config

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._config[CONF_TEXT_LANGUAGE]

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return ["zh", "en", "ja"]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return a dict include default options."""
        return {
            "speed": self._config[CONF_SPEED],
        }

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return ["speed"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load TTS audio."""
        websession = async_get_clientsession(self.hass)
        
        params = {
            "refer_wav_path": self._config[CONF_REFER_WAV_PATH],
            "prompt_text": self._config[CONF_PROMPT_TEXT],
            "prompt_language": self._config[CONF_PROMPT_LANGUAGE],
            "text": message,
            "text_language": language,
            "top_k": self._config[CONF_TOP_K],
            "top_p": self._config[CONF_TOP_P],
            "temperature": self._config[CONF_TEMPERATURE],
            "speed": options.get("speed", self._config[CONF_SPEED]),
            "sample_steps": 32,
            "if_sr": "false",
        }
        
        base_url = f"http://{self._config[CONF_HOST]}:{self._config[CONF_PORT]}/"
        request_url = base_url + "?" + urlencode(params)

        _LOGGER.debug("Requesting TTS from GPT-SoVITS: %s", request_url)

        try:
            # --- THE FIX IS HERE ---
            # Corrected 'aiohotp' to 'aiohttp'
            timeout = aiohttp.ClientTimeout(total=300)

            async with websession.get(request_url, timeout=timeout) as resp:
                if resp.status != HTTPStatus.OK:
                    error_text = await resp.text()
                    _LOGGER.error(
                        "Error from GPT-SoVITS API: %s - %s",
                        resp.status,
                        error_text,
                    )
                    return (None, None)

                _LOGGER.info("Successfully received audio stream from GPT-SoVITS.")
                
                audio_data = await resp.read()
                return ("wav", audio_data)

        except aiohttp.ClientError as err:
            _LOGGER.error("aiohttp client error: %s", err)
            return (None, None)
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to GPT-SoVITS API at %s", base_url)
            return (None, None)
        except Exception as err:
            _LOGGER.error("Unknown error occurred: %s", err)
            return (None, None)