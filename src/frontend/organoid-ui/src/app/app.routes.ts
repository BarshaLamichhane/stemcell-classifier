import { Routes } from '@angular/router';
import { InferenceUiDoppl } from './inference-ui-doppl/inference-ui-doppl';
import { InferenceUiCorintis } from './inference-ui-corintis/inference-ui-corintis';

export const routes: Routes = [
    { path: 'predict/dopplsa', component: InferenceUiDoppl},
    { path: 'predict/corontissa', component: InferenceUiCorintis},
    { path: '', redirectTo: 'predict/corontissa', pathMatch: 'full' },
    { path: '**', redirectTo: 'predict/corontissa' }
    
];
