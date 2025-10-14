import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Auth } from '../auth';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class Header {
  isLoggedIn$: Observable<boolean>;

  constructor(private authService: Auth, private router: Router) {
    this.isLoggedIn$ = this.authService.isLoggedIn$;
  }

  logout(event: MouseEvent): void {
    event.preventDefault();
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
