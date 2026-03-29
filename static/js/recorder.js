/**
 * recorder.js
 *
 * Browser MediaRecorder wrapper for VoiceTasks.
 *
 * This module is loaded on the dashboard page. The primary recording
 * logic is handled by the Alpine.js dashboard() component defined
 * inline in dashboard/index.html. This file provides additional
 * utility functions and a standalone VoiceRecorder class that can be
 * used independently of Alpine.
 */

'use strict';

/**
 * VoiceRecorder — standalone class wrapping the browser MediaRecorder API.
 *
 * Usage:
 *   const recorder = new VoiceRecorder();
 *   await recorder.start();
 *   const blob = await recorder.stop(); // returns audio Blob
 */
class VoiceRecorder {
  constructor(options = {}) {
    this.mimeType = options.mimeType || VoiceRecorder.preferredMimeType();
    this.mediaRecorder = null;
    this.chunks = [];
    this.stream = null;
    this.isRecording = false;
    this._stopResolve = null;
  }

  /**
   * Pick the best supported MIME type in this browser.
   * @returns {string}
   */
  static preferredMimeType() {
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/mp4',
    ];
    for (const type of candidates) {
      if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }
    return 'audio/webm'; // fallback
  }

  /**
   * Request microphone access and start recording.
   * @returns {Promise<void>}
   * @throws {Error} if microphone permission is denied
   */
  async start() {
    if (this.isRecording) {
      throw new Error('Already recording.');
    }

    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    this.chunks = [];

    const options = {};
    if (MediaRecorder.isTypeSupported(this.mimeType)) {
      options.mimeType = this.mimeType;
    }

    this.mediaRecorder = new MediaRecorder(this.stream, options);

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.chunks.push(event.data);
      }
    };

    this.mediaRecorder.onstop = () => {
      if (this._stopResolve) {
        const blob = new Blob(this.chunks, { type: this.mediaRecorder.mimeType || this.mimeType });
        this._stopResolve(blob);
        this._stopResolve = null;
      }
    };

    this.mediaRecorder.start(100); // collect data every 100ms
    this.isRecording = true;
  }

  /**
   * Stop recording and return the audio Blob.
   * @returns {Promise<Blob>}
   */
  stop() {
    return new Promise((resolve, reject) => {
      if (!this.isRecording || !this.mediaRecorder) {
        reject(new Error('Not currently recording.'));
        return;
      }

      this._stopResolve = resolve;
      this.mediaRecorder.stop();
      this.isRecording = false;

      // Release microphone tracks
      if (this.stream) {
        this.stream.getTracks().forEach((track) => track.stop());
        this.stream = null;
      }
    });
  }

  /**
   * Cancel recording without returning data.
   */
  cancel() {
    if (this.mediaRecorder && this.isRecording) {
      this._stopResolve = null;
      this.mediaRecorder.stop();
      this.isRecording = false;
    }
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    this.chunks = [];
  }
}

/**
 * Send an audio Blob to the backend transcription endpoint.
 *
 * @param {Blob} audioBlob - The recorded audio.
 * @param {string} language - BCP-47 language code.
 * @param {string} csrfToken - Django CSRF token.
 * @returns {Promise<{transcription: string, voice_note_id: number}>}
 */
async function uploadAudioForTranscription(audioBlob, language = 'en', csrfToken = '') {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('language', language);

  const response = await fetch('/voice/transcribe/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken || getCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// Expose for use from inline scripts
window.VoiceRecorder = VoiceRecorder;
window.uploadAudioForTranscription = uploadAudioForTranscription;
