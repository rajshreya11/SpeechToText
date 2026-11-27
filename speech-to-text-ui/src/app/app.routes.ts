
import { Routes } from '@angular/router';

import { Home } from './pages/home/home';
import { Transcribe } from './pages/transcribe/transcribe';
import { History } from './pages/history/history';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'home', component: Home },
  { path: 'transcribe', component: Transcribe },
  { path: 'history', component: History },
  { path: '**', component: Home }
];
