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

export interface TrainingStatus {
  status:{

    epoch: number;
    total_epochs: number;
    loss: number;
    loss_history: number[];
    status: string; // e.g., 'running', 'completed'
  }
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  // update if your backend uses different host/port
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  predictBloodCellType(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<PredictionResponse>(`${this.baseUrl}/predict`, formData);
  }

  filterCells(cellType: string, threshold: number) {
    return this.http.post(`${this.baseUrl}/filter`, {
      cell_type: cellType,
      threshold: threshold
    });
  }

  getMetricsStream(): EventSource {
    return new EventSource(`${this.baseUrl}/metrics/stream`);
  }

}
