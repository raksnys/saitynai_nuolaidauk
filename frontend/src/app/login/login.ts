import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Auth } from '../auth';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  email = '';
  password = '';

  constructor(private authService: Auth, private router: Router) {}

  onSubmit() {
    this.authService.login({
      email: this.email,
      password: this.password
    }).subscribe({
      next: (response: any) => {
        console.log('Login successful', response);
        // Handle successful login, e.g., store token and redirect
        this.router.navigate(['/my-profile']);
      },
      error: error => {
        console.error('Login failed', error);
        // Handle login error
      }
    });
  }
}
