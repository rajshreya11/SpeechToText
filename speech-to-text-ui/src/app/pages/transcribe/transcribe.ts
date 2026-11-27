
import { Component, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranscriptionService } from '../../services/transcription.service';

@Component({
  selector: 'app-transcribe',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './transcribe.html',
  styleUrl: './transcribe.css'
})
export class Transcribe implements OnDestroy {

  transcript = '';
  interimTranscript = '';

  isRecording = false;
  isSaving = false;

  selectedLanguage = 'hi-IN';

  errorMessage = '';
  successMessage = '';

  private mediaRecorder?: MediaRecorder;
  private mediaStream?: MediaStream;

  private audioChunks: Blob[] = [];
  private previewInProgress = false;

  constructor(
    private transcriptionService: TranscriptionService,
    private cdr: ChangeDetectorRef
  ) {}


  // START RECORDING
  async startRecording(): Promise<void> {

    this.errorMessage = '';
    this.successMessage = '';
    this.transcript = '';
    this.interimTranscript = '';
    this.audioChunks = [];

    try {

      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: true
      });

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      this.mediaRecorder = new MediaRecorder(this.mediaStream, {
        mimeType
      });

      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {

        if (event.data && event.data.size > 0) {

          this.audioChunks.push(event.data);

          if (this.isRecording) {
            this.requestPreview();
          }
        }
      };

      this.mediaRecorder.onstop = () => {

        const audioBlob = new Blob(this.audioChunks, {
          type: this.mediaRecorder?.mimeType || 'audio/webm'
        });

        this.releaseMicrophone();

        if (audioBlob.size > 0) {
          this.uploadAudio(audioBlob);
        } else {
          this.errorMessage = 'No audio recorded. Please try again.';
          this.isSaving = false;
          this.cdr.detectChanges();
        }
      };

      this.mediaRecorder.onerror = () => {
        this.errorMessage = 'Recording failed. Please try again.';
        this.isRecording = false;
        this.isSaving = false;
        this.releaseMicrophone();
        this.cdr.detectChanges();
      };

      // Collect audio chunks every 5 seconds
      this.mediaRecorder.start(5000);

      this.isRecording = true;
      this.cdr.detectChanges();

    } catch (error) {

      console.error('Microphone error:', error);

      this.errorMessage =
        'Microphone access denied. Please allow microphone permission.';

      this.isRecording = false;
      this.isSaving = false;

      this.releaseMicrophone();
      this.cdr.detectChanges();
    }
  }


  // STOP RECORDING
  stopRecording(): void {

    if (
      this.mediaRecorder &&
      this.mediaRecorder.state !== 'inactive'
    ) {

      this.isRecording = false;
      this.isSaving = true;

      this.mediaRecorder.stop();

      this.cdr.detectChanges();
    }
  }


  // PREVIEW TRANSCRIPTION
  private requestPreview(): void {

    if (
      !this.isRecording ||
      this.previewInProgress ||
      this.audioChunks.length === 0
    ) {
      return;
    }

    this.previewInProgress = true;

    const audioBlob = new Blob(this.audioChunks, {
      type: this.mediaRecorder?.mimeType || 'audio/webm'
    });

    const filename = 'recording.webm';

    this.transcriptionService
      .previewTranscription(
        audioBlob,
        filename,
        this.selectedLanguage
      )
      .subscribe({

        next: (response) => {

          if (this.isRecording) {
            this.interimTranscript = response.original_text || '';
            this.cdr.detectChanges();
          }

          this.previewInProgress = false;
        },

        error: (error) => {

          console.error('Preview transcription error:', error);

          this.previewInProgress = false;
        }

      });
  }


  // FINAL TRANSCRIPTION AND DATABASE SAVE
  private uploadAudio(audioBlob: Blob): void {

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const filename = 'recording.webm';

    this.transcriptionService
      .transcribeAudio(
        audioBlob,
        filename,
        this.selectedLanguage
      )
      .subscribe({

        next: (response) => {

          this.transcript = response.original_text;
          this.interimTranscript = '';

          this.successMessage =
            `Transcription successful! Record ID: ${response.id}`;

          this.isSaving = false;

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error('Final transcription error:', error);

          this.errorMessage =
            error.error?.detail ||
            'Transcription failed. Please try again.';

          this.isSaving = false;

          this.cdr.detectChanges();
        }

      });
  }


  // CHANGE LANGUAGE
  changeLanguage(language: string): void {

    if (this.isRecording) {
      this.stopRecording();
    }

    this.selectedLanguage = language;

    this.errorMessage = '';
    this.successMessage = '';

    this.cdr.detectChanges();
  }


  // CLEAR TRANSCRIPT
  clearTranscript(): void {

    this.transcript = '';
    this.interimTranscript = '';

    this.errorMessage = '';
    this.successMessage = '';

    this.cdr.detectChanges();
  }


  // MANUAL SAVE TRANSCRIPT
  saveTranscript(): void {

    if (!this.transcript.trim()) {
      this.errorMessage = 'There is no transcript to save.';
      return;
    }

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const language =
      this.selectedLanguage === 'hi-IN' ? 'Hindi' : 'English';

    this.transcriptionService
      .saveTranscription({
        original_text: this.transcript,
        language: language
      })
      .subscribe({

        next: (response) => {

          this.successMessage =
            `Transcript saved successfully! Record ID: ${response.id}`;

          this.isSaving = false;
          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error('Save transcript error:', error);

          this.errorMessage =
            'Failed to save transcript. Please try again.';

          this.isSaving = false;
          this.cdr.detectChanges();
        }

      });
  }


  // RELEASE MICROPHONE
  private releaseMicrophone(): void {

    if (this.mediaStream) {

      this.mediaStream.getTracks().forEach(track => {
        track.stop();
      });

      this.mediaStream = undefined;
    }
  }


  // COMPONENT CLEANUP
  ngOnDestroy(): void {

    if (
      this.mediaRecorder &&
      this.mediaRecorder.state !== 'inactive'
    ) {
      this.mediaRecorder.stop();
    }

    this.releaseMicrophone();
  }

}
