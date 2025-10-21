import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Auth } from '../auth';
import confetti from 'canvas-confetti';

interface DiscountModerationDTO {
  id: number;
  name: string;
  description: string;
  discount_type: 'percentage' | 'fixed';
  value: string;
  target_type: 'product' | 'category' | 'brand' | 'store';
  brand?: number | null;
  store?: number | null;
  category?: number | null;
  product?: number | null;
  starts_at: string;
  ends_at: string;
  status: 'in_review' | 'approved' | 'denied' | string; // backend stores lowercase; UI will map to labels
  submitted_by?: number | null;
  created_at: string;
}

@Component({
  selector: 'app-discounts-moderation',
  standalone: true,
  imports: [CommonModule, DatePipe, RouterModule],
  templateUrl: './discounts-moderation.html',
  styleUrls: ['./discounts-moderation.css']
})
export class DiscountsModerationComponent implements OnInit {
  items: DiscountModerationDTO[] = [];
  loading = false;
  error: string | null = null;
  updatingId: number | null = null;
  private api = `${environment.apiUrl}/catalog/discounts/moderation/`;

  constructor(
    private http: HttpClient,
    private auth: Auth,
    private cdr: ChangeDetectorRef
  ) {}

  get canModerate(): boolean {
    const role = this.auth.getRole();
    return role === 'admin' || role === 'moderator';
  }

  ngOnInit(): void {
    if (!this.canModerate) {
      this.error = 'Unauthorized';
      return;
    }
    this.fetch();
  }

  fetch(): void {
    this.loading = true;
    this.http.get<DiscountModerationDTO[]>(this.api, { withCredentials: true }).subscribe({
      next: (data) => { this.items = data; this.loading = false; this.cdr.detectChanges(); },
      error: (e) => { this.error = e?.error?.detail || 'Failed to load discounts'; this.loading = false; this.cdr.detectChanges(); }
    });
  }

  private triggerConfetti(): void {
    confetti.create(undefined, { resize: true })({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
  }

  labelStatus(s: string): string {
    const up = s?.toUpperCase();
    if (up === 'IN_REVIEW') return 'IN_REVIEW';
    if (up === 'APPROVED') return 'APPROVED';
    if (up === 'DENIED') return 'DENIED';
    return up || s;
  }

  setStatus(d: DiscountModerationDTO, status: 'approved'|'denied') {
    const url = `${this.api}${d.id}/`;
    this.updatingId = d.id;
    this.http.patch<DiscountModerationDTO>(url, { status }, { withCredentials: true }).subscribe({
      next: (updated) => {
        const idx = this.items.findIndex(x => x.id === d.id);
        if (idx !== -1) {
          this.items = [...this.items.slice(0, idx), updated, ...this.items.slice(idx + 1)];
          this.triggerConfetti();
        }
        this.updatingId = null; this.cdr.detectChanges();
      },
      error: (e) => { this.updatingId = null; this.cdr.detectChanges(); alert('Failed to update'); }
    });
  }

  // Derived lists for UI sections
  get inReviewItems(): DiscountModerationDTO[] {
    return (this.items || []).filter(i => this.labelStatus(i.status) === 'IN_REVIEW');
  }

  get approvedItems(): DiscountModerationDTO[] {
    return (this.items || []).filter(i => this.labelStatus(i.status) === 'APPROVED');
  }
}
