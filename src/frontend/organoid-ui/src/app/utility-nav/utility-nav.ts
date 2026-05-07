import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, NgZone } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { ApiService, PredictionResponse } from '../api/api.service';
import { BehaviorSubject } from 'rxjs';
import { Chart } from 'chart.js/auto';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-utility-nav',
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './utility-nav.html',
  styleUrl: './utility-nav.scss'
})
export class UtilityNav {

  // ================= STATE =================
  selectedFile!: File;
  result!: PredictionResponse;
  imagePreview!: string;
  loading$ = new BehaviorSubject<boolean>(false);

  selectedCellType = 'EOSINOPHIL';
  threshold = 0.8;
  filterResults: any[] = [];

  // training
  isTraining = false;
  trainingCompleted = false;

  epoch = 0;
  total = 18;
  loss = 0;


  logs: string[] = [];

  metricsEventSource: any;
  chart: any;
  lossHistory: number[] = [];

  constructor(
    private api: ApiService,
    private ngZone: NgZone,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  // ================= CHART INIT =================
  initChart() {
    setTimeout(() => {
      const canvas = document.getElementById('lossChart') as HTMLCanvasElement;

      if (!canvas) return;

      this.chart = new Chart(canvas, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Training Loss',
            data: [],
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false, // IMPORTANT
          animation: false
        }
      });
    }, 0);
  }

  // ================= TRAINING =================
  replayTraining() {

  this.isTraining = true;
  this.trainingCompleted = false;

  // IMPORTANT: new array reference
  this.logs = [];
  this.logs = [...this.logs, '> Starting training...'];

  this.lossHistory = [];

  this.initChart();

  this.metricsEventSource = this.api.getMetricsStream();

  this.metricsEventSource.onmessage = (e: MessageEvent) => {

    const data = JSON.parse(e.data);

    if (data.status === 'completed') {

      this.ngZone.run(() => {
        this.logs = [...this.logs, '> Training completed '];
        //this.isTraining = false;
        this.trainingCompleted = true;
        this.cdr.detectChanges(); //  FORCE UI to UPDATE
      });

      this.metricsEventSource.close();
      return;
    } 

    this.ngZone.run(() => {

      this.epoch = data.epoch;
      this.total = data.total_epochs;
      this.loss = data.loss;

      // This is important: immutable update for fixing UI rendering issues
      this.logs = [
        ...this.logs,
        `> Epoch ${this.epoch}/${this.total} - Loss: ${this.loss.toFixed(4)}`
      ];
      console.log(`Epoch ${this.epoch}/${this.total} - Loss: ${this.loss.toFixed(4)}`);

      this.lossHistory.push(this.loss);

      if (this.chart) {
        this.chart.data.labels.push(this.epoch);
        this.chart.data.datasets[0].data.push(this.loss);
        this.chart.update();
      }

      // force angular to render DOM immediately
      this.cdr.detectChanges();
    });
  };
}
  // ================= FILTER =================
  filter() {
    this.filterResults = [];
    this.loading$.next(true);

    this.api.filterCells(this.selectedCellType, this.threshold)
      .subscribe((res: any) => {
        this.filterResults = res.matched_files;
        this.loading$.next(false);
      });
  }

  // ================= PREDICT =================
  predict() {
    if (!this.selectedFile) return;

    this.loading$.next(true);

    this.api.predictBloodCellType(this.selectedFile)
      .subscribe({
        next: (res) => {
          this.result = res;
          this.loading$.next(false);
        },
        error: (err) => {
          console.error(err);
          this.loading$.next(false);
        }
      });
  }
}