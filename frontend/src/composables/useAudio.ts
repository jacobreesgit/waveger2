import { ref, watch, onUnmounted } from "vue";
import { Howl } from "howler";

export function useAudio() {
  // Audio state
  const sounds = ref<Record<number, Howl>>({});
  const playingTrackId = ref<number | null>(null);
  const audioProgress = ref<Record<number, number>>({});
  const volume = ref<number>(0.8); // Default volume

  // Stop any currently playing audio
  function stopCurrentAudio() {
    if (playingTrackId.value !== null && sounds.value[playingTrackId.value]) {
      sounds.value[playingTrackId.value].stop();
      playingTrackId.value = null;
    }
  }

  // Play preview if available
  function playPreview(previewUrl: string | null | undefined, trackId: number) {
    // Stop current audio if playing
    if (playingTrackId.value !== null) {
      stopCurrentAudio();

      // If clicking on same track, just stop it
      if (playingTrackId.value === trackId) {
        return;
      }
    }

    if (previewUrl) {
      try {
        // Create a new Howl instance if it doesn't exist
        if (!sounds.value[trackId]) {
          sounds.value[trackId] = new Howl({
            src: [previewUrl],
            html5: true, // Use HTML5 Audio to stream the audio
            volume: volume.value,
            onplay: () => {
              playingTrackId.value = trackId;
              audioProgress.value[trackId] = 0;
              // Update progress while playing
              const progressInterval = setInterval(() => {
                if (sounds.value[trackId]) {
                  const progress =
                    sounds.value[trackId].seek() /
                    sounds.value[trackId].duration();
                  audioProgress.value[trackId] = progress * 100;
                }
              }, 100);

              // Store the interval ID on the Howl instance for cleanup
              (sounds.value[trackId] as any)._progressInterval =
                progressInterval;
            },
            onend: () => {
              if ((sounds.value[trackId] as any)._progressInterval) {
                clearInterval((sounds.value[trackId] as any)._progressInterval);
              }
              audioProgress.value[trackId] = 0;
              playingTrackId.value = null;
            },
            onstop: () => {
              if ((sounds.value[trackId] as any)._progressInterval) {
                clearInterval((sounds.value[trackId] as any)._progressInterval);
              }
              audioProgress.value[trackId] = 0;
            },
          });
        } else {
          // Update volume in case it changed
          sounds.value[trackId].volume(volume.value);
        }

        // Play the sound
        sounds.value[trackId].play();
      } catch (error) {
        console.error("Error playing audio:", error);
      }
    }
  }

  // Update volume for current audio
  watch(volume, (newVolume) => {
    if (playingTrackId.value !== null && sounds.value[playingTrackId.value]) {
      sounds.value[playingTrackId.value].volume(newVolume);
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
    // Stop and unload all sounds
    Object.values(sounds.value).forEach((sound) => {
      sound.stop();
      sound.unload();
      // Clear any progress intervals
      if ((sound as any)._progressInterval) {
        clearInterval((sound as any)._progressInterval);
      }
    });

    sounds.value = {};
    playingTrackId.value = null;
  });

  return {
    playingTrackId,
    audioProgress,
    volume,
    stopCurrentAudio,
    playPreview,
    getAudioInfo,
    // Keep setupAudioContext in the return object for API compatibility
    setupAudioContext: () => {}, // No-op as Howler.js handles this internally
  };
}
