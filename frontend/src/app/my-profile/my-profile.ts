import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Auth } from '../auth';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-my-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './my-profile.html',
  styleUrls: ['./my-profile.css']
})
export class MyProfile implements OnInit {
  user: any;
  current_password = '';
  new_password = '';
  confirm_password = '';

  constructor(private authService: Auth, private cdr: ChangeDetectorRef) {}

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
}
