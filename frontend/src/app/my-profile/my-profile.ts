import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Auth } from '../auth';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WishlistService, WishlistItemDTO } from '../services/wishlist.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-my-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './my-profile.html',
  styleUrls: ['./my-profile.css']
})
export class MyProfile implements OnInit {
  user: any;
  current_password = '';
  new_password = '';
  confirm_password = '';
  wishlist: WishlistItemDTO[] = [];
  isLoadingWishlist = true;
  // Testing: tokens
  jwtLocal: string | null = null;
  jwtCookieReadable: string | null = null; // will be null/empty because of HttpOnly
  refreshCookieReadable: string | null = null; // will be null/empty because of HttpOnly
  lastRefreshTokenFromBody: string | null = null;
  lastRefreshResult: {
    beforeJwtPreview?: string | null;
    afterJwtPreview?: string | null;
    beforeRefreshPreview?: string | null;
    afterRefreshPreview?: string | null;
    accessChanged?: boolean;
    refreshChanged?: boolean;
    beforeAccessIat?: string;
    afterAccessIat?: string;
  } = {};

  constructor(private authService: Auth, private cdr: ChangeDetectorRef, private wishlistService: WishlistService) {}

  ngOnInit() {
    this.authService.getUser().subscribe({
      next: (response: any) => {
        this.user = response;
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Failed to get user profile', error);
      }
    });

    this.wishlistService.getWishlist().subscribe({
      next: (items) => {
        this.wishlist = items;
        this.isLoadingWishlist = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to load wishlist', err);
        this.isLoadingWishlist = false;
        this.cdr.detectChanges();
      }
    });

    // Initialize token testing state
    this.loadTokenState();
    this.authService.lastRefreshToken$.subscribe(t => {
      this.lastRefreshTokenFromBody = t;
      this.cdr.detectChanges();
    });
  }

  onChangePassword() {
    if (this.new_password !== this.confirm_password) {
      console.error('New passwords do not match');
      return;
    }

    this.authService.changePassword({
      current_password: this.current_password,
      new_password: this.new_password
    }).subscribe({
      next: (response: any) => {
        console.log('Password changed successfully', response);
        // Optionally, show a success message to the user
      },
      error: (error: any) => {
        console.error('Failed to change password', error);
        // Optionally, show an error message to the user
      }
    });
  }

  // -------------- TESTING: Tokens --------------
  loadTokenState() {
    this.jwtLocal = this.authService.getAuthToken();
    // HttpOnly cookies are not readable via document.cookie; these will be blank/null
    this.jwtCookieReadable = this.getCookie('jwt');
    this.refreshCookieReadable = this.getCookie('refresh_jwt');
    this.lastRefreshTokenFromBody = this.authService.getLastRefreshToken();
  }

  onRefreshTokens() {
    const beforeJwt = this.authService.getAuthToken();
    const beforeRefresh = this.authService.getLastRefreshToken();

    this.authService.refreshToken().subscribe({
      next: (resp) => {
        // Update local snapshots
        this.loadTokenState();

        const afterJwt = this.authService.getAuthToken();
        const afterRefresh = this.authService.getLastRefreshToken();

        this.lastRefreshResult = {
          beforeJwtPreview: this.preview(beforeJwt),
          afterJwtPreview: this.preview(afterJwt),
          beforeRefreshPreview: this.preview(beforeRefresh),
          afterRefreshPreview: this.preview(afterRefresh),
          accessChanged: beforeJwt !== afterJwt,
          refreshChanged: beforeRefresh !== afterRefresh,
          beforeAccessIat: beforeJwt ? this.humanIat(beforeJwt) : undefined,
          afterAccessIat: afterJwt ? this.humanIat(afterJwt) : undefined,
        };

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to refresh token', err);
      }
    });
  }

  private preview(token: string | null | undefined): string | null {
    if (!token) return null;
    const start = token.slice(0, 16);
    const end = token.slice(-8);
    return `${start}...${end}`;
  }

  private humanIat(jwt: string): string {
    try {
      const payload = JSON.parse(atob(jwt.split('.')[1] || ''));
      const iatSec: number | undefined = payload?.iat ? (typeof payload.iat === 'number' ? payload.iat : undefined) : undefined;
      if (!iatSec) return 'n/a';
      const date = new Date(iatSec * 1000);
      return date.toLocaleString();
    } catch {
      return 'n/a';
    }
  }

  private getCookie(name: string): string | null {
    if (typeof document === 'undefined') return null;
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }
}
