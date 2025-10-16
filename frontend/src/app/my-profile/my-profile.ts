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
