import { Routes } from '@angular/router';
import { ImageUploadComponent } from './image-upload/image-upload';
import { ResultComponent } from './results/results'

export const routes: Routes = [
    { path: '', component: ImageUploadComponent },
    { path: 'result', component: ResultComponent },
    { path: '**', redirectTo: '' }
];
