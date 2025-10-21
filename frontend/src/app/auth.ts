import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private apiUrl = environment.apiUrl;
  private authState = new BehaviorSubject<boolean>(this.hasToken());
  private roleState = new BehaviorSubject<string | null>(this.getStoredRole());
  // For testing/diagnostics: keep the last refresh token returned by backend (also set as HttpOnly cookie)
  private lastRefreshTokenState = new BehaviorSubject<string | null>(null);
  
  isLoggedIn$ = this.authState.asObservable();
  role$ = this.roleState.asObservable();
  lastRefreshToken$ = this.lastRefreshTokenState.asObservable();

  constructor(private http: HttpClient) {
    // ensure role is consistent with current JWT on startup
    const jwt = this.getAuthToken();
    if (jwt) {
      const roleFromJwt = this.decodeRole(jwt);
      if (roleFromJwt && roleFromJwt !== this.getStoredRole()) {
        localStorage.setItem('role', roleFromJwt);
        this.roleState.next(roleFromJwt);
      }
    }
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('jwt');
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData);
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials, { withCredentials: true }).pipe(
      tap((response: any) => {
        localStorage.setItem('jwt', response.jwt);
        const role = this.decodeRole(response.jwt);
        if (role) {
          localStorage.setItem('role', role);
          this.roleState.next(role);
        }
        // capture refresh token returned in body (also set as HttpOnly cookie)
        if (response?.refresh_token) {
          this.lastRefreshTokenState.next(response.refresh_token);
        }
        this.authState.next(true);
      })
    );
  }

  logout() {
    localStorage.removeItem('jwt');
    localStorage.removeItem('role');
    this.authState.next(false);
  }

  getAuthToken(): string | null {
    return localStorage.getItem('jwt');
  }

  getRole(): string | null {
    return this.roleState.value;
  }

  getUser(): Observable<any> {
    return this.http.get(`${this.apiUrl}/user`, { withCredentials: true });
  }

  changePassword(passwords: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/change-password`, passwords, { withCredentials: true });
  }

  refreshToken(): Observable<any> {
    return this.http.post(`${this.apiUrl}/refresh`, {}, { withCredentials: true }).pipe(
      tap((response: any) => {
        localStorage.setItem('jwt', response.jwt);
        const role = this.decodeRole(response.jwt);
        if (role) {
          localStorage.setItem('role', role);
          this.roleState.next(role);
        }
        if (response?.refresh_token) {
          this.lastRefreshTokenState.next(response.refresh_token);
        }
      })
    );
  }

  private getStoredRole(): string | null {
    return localStorage.getItem('role');
  }

  private decodeRole(jwt: string): string | null {
    try {
      const payload = JSON.parse(atob(jwt.split('.')[1] || ''));
      return payload?.role ?? null;
    } catch {
      return null;
    }
  }

  // Testing helpers
  getLastRefreshToken(): string | null {
    return this.lastRefreshTokenState.value;
  }
}
