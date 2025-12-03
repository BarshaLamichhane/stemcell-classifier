import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-results',
  imports: [],
  templateUrl: './results.html',
  styleUrl: './results.scss',
})
export class Results {
  data: any = null;

  ngOnInit() {
    this.data = JSON.parse(localStorage.getItem('analysis') || 'null');
    // If similar_images are filenames pointing to backend static route, prefix with base url if needed
    if (this.data && this.data.similar_images && typeof this.data.similar_images[0] === 'string' && !this.data.similar_images[0].startsWith('data:')) {
      const base = 'http://127.0.0.1:8000/static/images/';
      this.data.similar_images = this.data.similar_images.map((p: string) => base + p);
    }
  }
}
