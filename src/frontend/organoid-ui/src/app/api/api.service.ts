import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

//@Injectable({ providedIn: 'root' })
export class ApiService {
  // update if your backend uses different host/port
  private BASE = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  predict(file: File): Observable<any> {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post(`${this.BASE}/predict`, fd);
  }

  // fallback: if predict does not return images, call search endpoint
  searchSimilar(file: File): Observable<any> {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post(`${this.BASE}/search`, fd);
  }

  // fallback: fetch image by index (requires backend support /image/{idx})
  getImageByIndex(idx: number): Observable<Blob> {
    const headers = new HttpHeaders({ Accept: 'image/*' });
    return this.http.get(`${this.BASE}/image/${idx}`, { responseType: 'blob', headers });
  }
}
