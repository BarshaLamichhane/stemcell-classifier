import { Component } from '@angular/core';
import { ApiService } from '../api/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-upload',
  templateUrl: './image-upload.html',
  styleUrls: ['./image-upload.scss']
})
export class ImageUploadComponent {
  file?: File;
  preview?: string;
  loading = false;
  error?: string;

  constructor(private api: ApiService, private router: Router) {}

  onFile(evt: any) {
    this.error = undefined;
    const f = evt.target.files?.[0];
    if (!f) return;
    this.file = f;

    const reader = new FileReader();
    reader.onload = e => this.preview = e.target?.result as string;
    reader.readAsDataURL(f);
  }

  analyze() {
    if (!this.file) return;
    this.loading = true;
    this.api.predict(this.file).subscribe({
      next: (res: any) => {
        this.loading = false;
        // If backend already returns similar_images (base64), we use it
        if (res.similar_images && res.similar_images.length > 0) {
          const payload = {
            original_base64: res.original_base64 || this.preview,
            mask_base64: res.mask_base64 || null,
            class_label: res.class_label || res.prediction || null,
            confidence: res.confidence || (res.probabilities ? res.probabilities[res.prediction] : null),
            similar_images: res.similar_images
          };
          localStorage.setItem('analysis', JSON.stringify(payload));
          this.router.navigate(['/result']);
          return;
        }

        // Otherwise fallback to /search -> returns indices/distances
        this.api.searchSimilar(this.file!).subscribe({
          next: (searchRes: any) => {
            // store search result and navigate; result component will fetch images individually
            const payload = {
              original_base64: this.preview,
              class_label: res.class || res.prediction || null,
              confidence: res.probabilities ? Math.max(...res.probabilities) : null,
              search_indices: searchRes.indices || [],
              search_distances: searchRes.distances || []
            };
            localStorage.setItem('analysis', JSON.stringify(payload));
            this.router.navigate(['/result']);
          },
          error: (err) => {
            this.loading = false;
            this.error = 'Prediction succeeded but similarity search failed.';
            console.error(err);
          }
        });
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
        this.error = 'Failed to call /predict. Is the backend running?';
      }
    });
  }
}
