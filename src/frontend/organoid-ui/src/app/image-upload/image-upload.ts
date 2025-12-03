import { Component } from '@angular/core';
import { ApiService } from '../api/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-image-upload',
  imports: [],
  templateUrl: './image-upload.html',
  styleUrl: './image-upload.scss',
})
export class ImageUpload {
  selectedFile?: File;
  previewUrl?: string;

  constructor(private api: ApiService, private router: Router) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    const reader = new FileReader();
    reader.onload = e => this.previewUrl = e.target?.result as string;
    reader.readAsDataURL(this.selectedFile!);
  }

  analyze() {
    if (!this.selectedFile) return;
    this.api.predictImage(this.selectedFile).subscribe(res => {
      // res should include original_base64, mask_base64, class_label, confidence, similar_images[]
      localStorage.setItem('analysis', JSON.stringify(res));
      this.router.navigate(['/result']);
    });
  }
}
