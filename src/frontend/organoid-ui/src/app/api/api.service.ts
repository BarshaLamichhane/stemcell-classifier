import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PredictionResponse {
  predictions: {
    predicted_label: string;
    predicted_class_name: string;
    confidence_scores: number;
  };
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  // update if your backend uses different host/port
  private baseUrl = 'http://localhost:8000/predict';

  constructor(private http: HttpClient) {}

  predictBloodCellType(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<PredictionResponse>(this.baseUrl, formData);
  }
}
