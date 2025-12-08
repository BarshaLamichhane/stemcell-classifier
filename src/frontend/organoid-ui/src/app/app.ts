import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  file: File | null = null;
  result: any;

  constructor(private http: HttpClient) {}

  onFileSelected(event: any) {
    this.file = event.target.files[0];
  }

  upload() {
    const formData = new FormData();
    formData.append("file", this.file!);

    this.http.post("http://localhost:8000/predict", formData)
      .subscribe(res => {
        this.result = res;
      });
  }
}
