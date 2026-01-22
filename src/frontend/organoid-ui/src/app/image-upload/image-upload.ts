import { AfterViewInit, Component, NgZone } from '@angular/core';
import { ApiService, PredictionResponse } from '../api/api.service';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';


@Component({
  selector: 'image-upload',
  templateUrl: './image-upload.html',
  styleUrls: ['./image-upload.scss'],
  imports: [RouterModule, RouterOutlet, CommonModule],
})
export class ImageUploadComponent{
  selectedFile!: File;
  result!: PredictionResponse;
  loading$ = new BehaviorSubject<boolean>(false);
  //loading = false;
  imagePreview!: string;

  constructor(private api: ApiService, private ngZone: NgZone, private router: Router) {}

  onFileSelected(evt: any) {
    this.selectedFile = evt.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
    this.imagePreview = reader.result as string;
    };
    reader.readAsDataURL(this.selectedFile);
  }
  clearImage() {
    this.selectedFile = null as any;
    this.imagePreview = '';
    this.result = null as any;
  }
  predict() {
    if (!this.selectedFile) return;

    this.loading$.next(true);  // set loading to true
              // reset previous result

    this.api.predictBloodCellType(this.selectedFile).subscribe({
      next: (response) => {
        this.result = response;
        this.loading$.next(false); // set loading to false
      },
      error: (err) => {
        console.error(err);
        this.loading$.next(false); // ensure spinner disappears even on error
      }
    });

      /*if (!this.selectedFile) return;

      this.loading = true;

      this.api.predictBloodCellType(this.selectedFile).subscribe({
        next: (response) => {
          this.ngZone.run(() => {
            this.result = response;
            this.loading = false;
          });
        },
        error: (err) => {
          this.ngZone.run(() => {
            console.error(err);
            this.loading = false;
          });
        }
      });*/
 }


}
