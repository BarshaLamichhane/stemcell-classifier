import { CommonModule } from '@angular/common';
import { Component, NgZone, ViewChild, ElementRef } from '@angular/core';
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

  // ================= VIEW =================
  @ViewChild('terminalBox') terminalBox!: ElementRef;

  // ================= STATE =================
  selectedFile!: File;
  result!: PredictionResponse;
  imagePreview!: string;
  loading$ = new BehaviorSubject<boolean>(false);

  selectedCellType = 'EOSINOPHIL';
  threshold = 0.8;
  filterResults: any[] = [];

  // ================= TRAINING =================
  isTraining = false;
  trainingCompleted = false;

  epoch = 0;
  total = 50;
  loss = 0;

  logs: string[] = [];
  metricsEventSource: any;

  chart: any;

  constructor(
    private api: ApiService,
    private ngZone: NgZone,
    private router: Router
  ) {}

  // ================= INIT CHART =================
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
          animation: false
        }
      });

    }, 0);
  }

  // ================= SCROLL =================
  scrollToBottom() {
    setTimeout(() => {
      if (this.terminalBox) {
        const el = this.terminalBox.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    }, 50);
  }

  // ================= TRAINING =================
  replayTraining() {

    this.isTraining = true;
    this.trainingCompleted = false;

    this.logs = ['> Starting training...'];

    this.initChart();

    if (this.chart) {
      this.chart.data.labels = [];
      this.chart.data.datasets[0].data = [];
      this.chart.update();
    }

    this.metricsEventSource = this.api.getMetricsStream();

    this.metricsEventSource.onmessage = (e: MessageEvent) => {

      const data = JSON.parse(e.data);

      // ================= DONE =================
      if (data.status === 'completed') {

        this.ngZone.run(() => {
          this.logs.push('> Training completed ✅');
          this.isTraining = false;
          this.trainingCompleted = true;
        });

        this.metricsEventSource.close();
        return;
      }

      // ================= EACH EPOCH =================
      this.ngZone.run(() => {

        this.epoch = data.epoch;
        this.total = data.total_epochs;
        this.loss = data.loss;

        // CLEAN SYNC LOG (start + middle + end)
        this.logs.push(`> Epoch ${this.epoch}/${this.total} started...`);
        this.logs.push(`  ↳ forward pass running...`);
        this.logs.push(`  ↳ backpropagation running...`);
        this.logs.push(`> Epoch ${this.epoch}/${this.total} finished — Loss: ${this.loss.toFixed(4)}`);

        // keep memory safe
        if (this.logs.length > 200) {
          this.logs = this.logs.slice(-200);
        }

        // update chart step-by-step
        if (this.chart) {
          this.chart.data.labels.push(this.epoch);
          this.chart.data.datasets[0].data.push(this.loss);
          this.chart.update();
        }

        this.scrollToBottom();
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
        error: () => this.loading$.next(false)
      });
  }
}