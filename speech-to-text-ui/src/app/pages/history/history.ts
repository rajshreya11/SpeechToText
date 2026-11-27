// import { Component } from '@angular/core';

// @Component({
//   imports: [],
//   selector: 'app-history',
//   styleUrl: './history.css',
//   templateUrl: './history.html',
// })
// export class History {}



import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import {
  Transcription,
  TranscriptionService
} from '../../services/transcription.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './history.html',
  styleUrl: './history.css'
})
export class History implements OnInit {

  transcriptions: Transcription[] = [];

  isLoading = false;
  errorMessage = '';
  successMessage = '';

  editingId: number | null = null;
  editedText = '';
  editedLanguage = '';

  constructor(
    private transcriptionService: TranscriptionService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadTranscriptions();
  }

  // READ: Load all records
  
loadTranscriptions(): void {
  this.isLoading = true;
  this.errorMessage = '';
  this.cdr.detectChanges();

  this.transcriptionService.getTranscriptions().subscribe({

    next: (data) => {
      this.transcriptions = data;
      this.isLoading = false;

      console.log('History loaded:', data);

      this.cdr.detectChanges();
    },

    error: (error) => {
      console.error('History API error:', error);

      this.errorMessage = 'Failed to load history.';
      this.isLoading = false;

      this.cdr.detectChanges();
    }

  });
}


  // Start editing
  startEdit(item: Transcription): void {
    this.editingId = item.id;
    this.editedText = item.original_text;
    this.editedLanguage = item.language || 'Hindi';

    this.successMessage = '';
    this.errorMessage = '';
  }

  // Cancel editing
  cancelEdit(): void {
    this.editingId = null;
    this.editedText = '';
    this.editedLanguage = '';
  }

  // UPDATE: Save changes
  updateTranscript(id: number): void {
    if (!this.editedText.trim()) {
      this.errorMessage = 'Transcript cannot be empty.';
      return;
    }

    this.transcriptionService.updateTranscription(id, {
      original_text: this.editedText.trim(),
      language: this.editedLanguage
    }).subscribe({
      next: () => {
        this.successMessage = 'Transcript updated successfully!';
        this.cancelEdit();
        this.loadTranscriptions();
      },
      error: (error) => {
        console.error('Update error:', error);
        this.errorMessage = 'Unable to update transcript.';
      }
    });
  }

  // DELETE: Remove record
  deleteTranscript(id: number): void {
    const confirmed = window.confirm(
      'Are you sure you want to delete this transcript?'
    );

    if (!confirmed) {
      return;
    }

    this.transcriptionService.deleteTranscription(id).subscribe({
      next: () => {
        this.transcriptions = this.transcriptions.filter(
          item => item.id !== id
        );

        this.successMessage = 'Transcript deleted successfully!';
        this.errorMessage = '';
      },
      error: (error) => {
        console.error('Delete error:', error);
        this.errorMessage = 'Unable to delete transcript.';
      }
    });
  }
}
