import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Auth } from '../auth';

@Component({
  selector: 'app-register',
  imports: [FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  name = '';
  email = '';
  password = '';

  constructor(private authService: Auth, private router: Router) {}

  onSubmit() {
    this.authService.register({
      name: this.name,
      email: this.email,
      password: this.password
    }).subscribe({
      next: response => {
        console.log('Registration successful', response);
        this.router.navigate(['/login']);

        // Handle successful registration, e.g., redirect to login
      },
      error: error => {
        console.error('Registration failed', error);
        // Handle registration error
      }
    });
  }
}
