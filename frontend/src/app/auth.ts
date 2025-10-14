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
  
  isLoggedIn$ = this.authState.asObservable();

  constructor(private http: HttpClient) { }

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
        localStorage.setItem('role', response.role);
        this.authState.next(true);
      })
    );
  }

  logout() {
    localStorage.removeItem('jwt');
    localStorage.removeItem('role');
    this.authState.next(false);
  }

  getUser(): Observable<any> {
    return this.http.get(`${this.apiUrl}/user`, { withCredentials: true });
  }

  changePassword(passwords: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/change-password`, passwords, { withCredentials: true });
  }

  refreshToken(): Observable<any> {
    return this.http.post(`${this.apiUrl}/refresh`, {}, { withCredentials: true });
  }
}
