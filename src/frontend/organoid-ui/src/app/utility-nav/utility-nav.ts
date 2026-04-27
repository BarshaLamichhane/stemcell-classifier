import { CommonModule } from '@angular/common';
import { Component, NgZone, OnInit } from '@angular/core';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { ApiService, PredictionResponse, TrainingStatus } from '../api/api.service';
import { BehaviorSubject } from 'rxjs/internal/BehaviorSubject';
import { Chart } from 'chart.js/auto';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-utility-nav',
  imports: [RouterModule, RouterOutlet, CommonModule, FormsModule],
  templateUrl: './utility-nav.html',
  styleUrl: './utility-nav.scss'
})
export class UtilityNav {

  selectedFile!: File;
  result!: PredictionResponse;
  loading$ = new BehaviorSubject<boolean>(false);
  //loading = false;
  imagePreview!: string;

  selectedCellType = 'EOSINOPHIL';
  threshold = 0.8;

  filterResults: any[] = [];

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

  filter() {
    this.filterResults = [];
    this.loading$.next(true);
    this.api.filterCells(this.selectedCellType, this.threshold)
      .subscribe((res: any) => {
        this.filterResults = res.matched_files;
        this.loading$.next(false);
        console.log(res);
      });
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
