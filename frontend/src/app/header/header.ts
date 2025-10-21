import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Auth } from '../auth';
import { Observable } from 'rxjs';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class Header {
  isLoggedIn$: Observable<boolean>;
  role$: Observable<string | null>;
  searchQuery = '';

  constructor(private authService: Auth, private router: Router) {
    this.isLoggedIn$ = this.authService.isLoggedIn$;
    this.role$ = this.authService.role$;
  }

  onSearch(): void {
    if (this.searchQuery.trim()) {
      this.router.navigate(['/search'], { queryParams: { q: this.searchQuery.trim() } });
      this.searchQuery = '';
    }
  }

  logout(event: MouseEvent): void {
    event.preventDefault();
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
