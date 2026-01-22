import { Routes } from '@angular/router';
import { ImageUploadComponent } from './image-upload/image-upload';
export const routes: Routes = [
    { path: 'predict', component: ImageUploadComponent },
    { path: '', redirectTo: 'predict', pathMatch: 'full' },
    { path: '**', redirectTo: 'predict' }
    
];
