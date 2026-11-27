
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Transcription {
  id: number;
  original_text: string;
  language: string | null;
  created_at: string;
}

export interface TranscriptionRequest {
  original_text: string;
  language: string;
}

export interface PreviewTranscription {
  original_text: string;
  language: string;
  language_probability: number;
}

@Injectable({
  providedIn: 'root'
})
export class TranscriptionService {

  private apiUrl = 'http://localhost:8000/api/transcriptions';

  constructor(private http: HttpClient) {}

  saveTranscription(data: TranscriptionRequest): Observable<Transcription> {
    return this.http.post<Transcription>(this.apiUrl, data);
  }

  getTranscriptions(): Observable<Transcription[]> {
    return this.http.get<Transcription[]>(this.apiUrl);
  }

  updateTranscription(
    id: number,
    data: TranscriptionRequest
  ): Observable<Transcription> {
    return this.http.put<Transcription>(`${this.apiUrl}/${id}`, data);
  }

  deleteTranscription(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  transcribeAudio(
    audio: Blob,
    filename: string,
    language: string
  ): Observable<Transcription> {

    const formData = new FormData();
    formData.append('file', audio, filename);
    formData.append('language', language);

    return this.http.post<Transcription>(
      `${this.apiUrl}/whisper`,
      formData
    );
  }

  previewTranscription(
    audio: Blob,
    filename: string,
    language: string
  ): Observable<PreviewTranscription> {

    const formData = new FormData();
    formData.append('file', audio, filename);
    formData.append('language', language);

    return this.http.post<PreviewTranscription>(
      `${this.apiUrl}/preview`,
      formData
    );
  }
}
