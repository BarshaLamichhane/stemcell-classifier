import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api/api.service';

@Component({
  selector: 'app-result',
  templateUrl: './results.html',
  styleUrls: ['./results.scss']
})
export class ResultComponent implements OnInit {
  data: any = null;
  similarImages: string[] = [];
  loadingSimilar = false;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    const raw = localStorage.getItem('analysis');
    if (!raw) return;
    this.data = JSON.parse(raw);

    // If similar images are already provided (base64), use them
    if (this.data.similar_images && this.data.similar_images.length) {
      this.similarImages = this.data.similar_images;
      return;
    }

    // Otherwise we have search indices -> we will call backend /image/{idx} to fetch thumbnails
    const indices = (this.data.search_indices && this.data.search_indices[0]) || [];
    if (indices && indices.length) {
      this.loadingSimilar = true;
      // fetch each image by index (backend must implement /image/{idx} that returns image blob)
      const promises = indices.map((idx: number) =>
        this.api.getImageByIndex(idx).toPromise()
          .then((blob: Blob) => {
            return new Promise<string>((resolve) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result as string);
              reader.readAsDataURL(blob);
            });
          })
          .catch(err => {
            console.error('image fetch failed', err);
            return '';
          })
      );

      Promise.all(promises).then((results) => {
        this.similarImages = results.filter(r => r);
        this.loadingSimilar = false;
      });
    }
  }
}
