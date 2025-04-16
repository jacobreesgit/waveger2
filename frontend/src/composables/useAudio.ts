import { ref, watch, onUnmounted } from "vue";

export function useAudio() {
  // Audio state
  const currentAudio = ref<HTMLAudioElement | null>(null);
  const playingTrackId = ref<number | null>(null);
  const audioProgress = ref<Record<number, number>>({});
  const volume = ref<number>(0.8); // Default volume

  // Web Audio API components
  const audioContext = ref<AudioContext | null>(null);
  const analyser = ref<AnalyserNode | null>(null);

  // Setup Web Audio API
  function setupAudioContext() {
    try {
      audioContext.value = new (window.AudioContext ||
        (window as any).webkitAudioContext)();
      analyser.value = audioContext.value.createAnalyser();
      analyser.value.connect(audioContext.value.destination);
    } catch (e) {
      console.warn("Web Audio API not supported:", e);
    }
  }

  // Stop any currently playing audio
  function stopCurrentAudio() {
    if (currentAudio.value) {
      currentAudio.value.pause();
      currentAudio.value = null;
      playingTrackId.value = null;
    }
  }

  // Play preview if available
  async function playPreview(
    previewUrl: string | null | undefined,
    trackId: number
  ) {
    // Stop current audio if playing
    if (currentAudio.value) {
      currentAudio.value.pause();
      currentAudio.value = null;

      // If clicking on same track, just stop it
      if (playingTrackId.value === trackId) {
        playingTrackId.value = null;
        return;
      }
    }

    if (previewUrl && audioContext.value) {
      try {
        // Resume audio context if suspended
        if (audioContext.value.state === "suspended") {
          await audioContext.value.resume();
        }

        // Create and configure audio element
        const audio = new Audio(previewUrl);
        audio.crossOrigin = "anonymous";
        audio.volume = volume.value;

        // Connect to audio analyzer
        const source = audioContext.value.createMediaElementSource(audio);
        source.connect(analyser.value as AnalyserNode);

        // Track progress
        audio.ontimeupdate = () => {
          if (audio.duration) {
            audioProgress.value[trackId] =
              (audio.currentTime / audio.duration) * 100;
          }
        };

        // Start playback
        await audio.play();
        currentAudio.value = audio;
        playingTrackId.value = trackId;
        audioProgress.value[trackId] = 0;

        // Reset when playback ends
        audio.onended = () => {
          playingTrackId.value = null;
          currentAudio.value = null;
          audioProgress.value[trackId] = 0;
        };
      } catch (error) {
        console.error("Error playing audio:", error);
      }
    }
  }

  // Update volume for current audio
  watch(volume, (newVolume) => {
    if (currentAudio.value) {
      currentAudio.value.volume = newVolume;
    }
  });

  // Get audio playback information
  function getAudioInfo(trackId: number) {
    const isPlaying = playingTrackId.value === trackId;
    const progress = audioProgress.value[trackId] ?? 0;

    return {
      isPlaying,
      progress: progress / 100,
    };
  }

  // Clean up resources
  onUnmounted(() => {
    stopCurrentAudio();
    if (audioContext.value && audioContext.value.state !== "closed") {
      audioContext.value.close();
    }
  });

  return {
    currentAudio,
    playingTrackId,
    audioProgress,
    volume,
    setupAudioContext,
    stopCurrentAudio,
    playPreview,
    getAudioInfo,
  };
}
