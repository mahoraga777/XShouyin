import io
import wave
import time
import logging
import threading
import pyaudio
import numpy as np
from evdev import UInput, ecodes as e
from faster_whisper import WhisperModel

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DictationService")

# -----------------------------------------------------------------------------
# Hardware Interaction Layer
# -----------------------------------------------------------------------------
class VirtualKeyboard:
    """Kernel-level virtual keyboard utilizing evdev and /dev/uinput."""
    
    def __init__(self):
        self.keymap = {
            'a': e.KEY_A, 'b': e.KEY_B, 'c': e.KEY_C, 'd': e.KEY_D,
            'e': e.KEY_E, 'f': e.KEY_F, 'g': e.KEY_G, 'h': e.KEY_H,
            'i': e.KEY_I, 'j': e.KEY_J, 'k': e.KEY_K, 'l': e.KEY_L,
            'm': e.KEY_M, 'n': e.KEY_N, 'o': e.KEY_O, 'p': e.KEY_P,
            'q': e.KEY_Q, 'r': e.KEY_R, 's': e.KEY_S, 't': e.KEY_T,
            'u': e.KEY_U, 'v': e.KEY_V, 'w': e.KEY_W, 'x': e.KEY_X,
            'y': e.KEY_Y, 'z': e.KEY_Z, ' ': e.KEY_SPACE,
            '.': e.KEY_DOT, ',': e.KEY_COMMA, '?': e.KEY_SLASH,
            '!': e.KEY_1, "'": e.KEY_APOSTROPHE, '-': e.KEY_MINUS
        }
        
        # Register capabilities with the kernel to authorize these specific events
        allowed_keys = list(set(self.keymap.values())) + [e.KEY_LEFTSHIFT]
        capabilities = {e.EV_KEY: allowed_keys}
        
        try:
            self.ui = UInput(events=capabilities, name="xshouyan-keyboard")
            logger.info("Virtual keyboard registered successfully.")
        except Exception as err:
            logger.critical(f"Failed to initialize UInput. Ensure permissions are set: {err}")
            raise

    def type_text(self, text: str) -> None:
        """Injects hardware-level keystrokes for the provided string."""
        if not text:
            return

        text = text.strip() + " " 
        
        for char in text:
            is_upper = char.isupper()
            char_lower = char.lower()

            if char_lower in self.keymap:
                keycode = self.keymap[char_lower]
                try:
                    if is_upper:
                        self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    
                    self.ui.write(e.EV_KEY, keycode, 1)
                    self.ui.write(e.EV_KEY, keycode, 0)
                    
                    if is_upper:
                        self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    
                    self.ui.syn()
                    time.sleep(0.01) # 10ms mechanical delay simulation
                except Exception as err:
                    logger.error(f"Hardware interrupt failed for '{char}': {err}")
            else:
                logger.debug(f"Unmapped character '{char}' dropped.")


# -----------------------------------------------------------------------------
# Data Processing Layer
# -----------------------------------------------------------------------------
class AudioCapturer:
    """Manages audio streams, Voice Activity Detection (VAD), and buffer allocation."""
    
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk_size = 1024
        
        # VAD Parameters
        self.threshold = 500
        self.silence_limit = int((self.rate / self.chunk_size) * 1.5)  # 1.5s of silence stops recording
        self.timeout_limit = int((self.rate / self.chunk_size) * 4.0)  # 4s of initial silence aborts
        self.max_record = int((self.rate / self.chunk_size) * 15.0)    # 15s absolute maximum

    def listen(self) -> io.BytesIO | None:
        """Captures audio until silence is detected or a timeout is reached."""
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(format=self.format, channels=self.channels, 
                                rate=self.rate, input=True, frames_per_buffer=self.chunk_size)
        except Exception as err:
            logger.error(f"Audio interface failure: {err}")
            audio.terminate()
            return None

        frames = []
        silent_chunks = 0
        total_chunks = 0
        is_speaking = False

        logger.info("Microphone active. Awaiting voice input...")
        
        try:
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                energy = np.abs(audio_data).mean()

                if energy > self.threshold:
                    is_speaking = True       
                    silent_chunks = 0      
                    frames.append(data)   
                elif is_speaking:
                    frames.append(data)
                    silent_chunks += 1
                    if silent_chunks > self.silence_limit:
                        logger.debug("VAD: Silence limit reached. Ending capture.")
                        break
                else:
                    silent_chunks += 1
                    if silent_chunks > self.timeout_limit:
                        logger.info("VAD: Request timed out (No speech detected).")
                        break
                
                if is_speaking:
                    total_chunks += 1
                    if total_chunks > self.max_record:
                        logger.warning("VAD: Maximum recording duration reached.")
                        break

        except Exception as err:
            logger.error(f"Stream interrupted: {err}")
            return None
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        if not frames or not is_speaking:
            return None

        # Pack raw frames into an in-memory WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(frames))
        
        wav_buffer.seek(0)
        return wav_buffer


class TranscriptionEngine:
    """Handles inference via the Faster-Whisper CTranslate2 backend."""
    
    def __init__(self):
        logger.info("Initializing ML models into memory (INT8 quant)...")
        # CPU initialization is fast and lightweight for the tiny model
        self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    def transcribe(self, wav_buffer: io.BytesIO) -> str:
        """Processes WAV bytes through the STT neural network."""
        try:
            segments, _ = self.model.transcribe(wav_buffer, beam_size=1, vad_filter=True)
            
            valid_text = []
            for segment in segments:
                if segment.no_speech_prob < 0.5:
                    valid_text.append(segment.text)
            
            return " ".join(valid_text).strip()
            
        except Exception as err:
            logger.error(f"Inference engine failure: {err}")
            return ""


# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
class DictationController:
    """Thread-safe controller managing the dictation lifecycle."""
    
    def __init__(self):
        self.keyboard = VirtualKeyboard()
        self.audio = AudioCapturer()
        self.stt = TranscriptionEngine()
        self._is_processing = False
        self._lock = threading.Lock()

    def _pipeline_worker(self) -> None:
        """Internal worker executing the I/O and ML workloads."""
        try:
            wav_buffer = self.audio.listen()
            if wav_buffer:
                text = self.stt.transcribe(wav_buffer)
                if text:
                    logger.info(f"Dictation Output: {text}")
                    self.keyboard.type_text(text)
                else:
                    logger.debug("Model output was empty.")
        finally:
            with self._lock:
                self._is_processing = False

    def trigger_async(self) -> None:
        """Spawns the dictation pipeline in a non-blocking daemon thread."""
        with self._lock:
            if self._is_processing:
                logger.debug("Trigger ignored: Pipeline is currently busy.")
                return
            self._is_processing = True

        # Daemon threads die automatically when the main program exits
        worker = threading.Thread(target=self._pipeline_worker, daemon=True, name="DictationWorker")
        worker.start()