import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ReportModerationDTO, ReportService } from '../services/report.service';
import { Auth } from '../auth';
import { ProductService } from '../services/product.service';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { RouterModule } from '@angular/router';
import confetti from 'canvas-confetti';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, DatePipe, RouterModule],
  templateUrl: './reports.html',
  styleUrls: ['./reports.css']
})
export class Reports implements OnInit {
  reports: ReportModerationDTO[] = [];
  loading = false;
  error: string | null = null;
  updatingId: number | null = null;
  productNames: Record<number, string> = {};

  constructor(
    private reportService: ReportService,
    private auth: Auth,
    private cdr: ChangeDetectorRef,
    private productService: ProductService
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
    this.fetchReports();
  }

  fetchReports(): void {
    this.loading = true;
    this.reportService.listReports().subscribe({
      next: (data) => {
        this.reports = data;
        this.loading = false;
        this.loadProductNames();
        this.cdr.detectChanges();
      },
      error: (e) => {
        this.error = e?.error?.error || 'Failed to load reports';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  private loadProductNames(): void {
    const ids = Array.from(new Set(
      this.reports
        .filter(r => !!r.product)
        .map(r => r.product as number)
        .filter(id => !(id in this.productNames))
    ));
    if (ids.length === 0) return;

    const calls = ids.map(id => this.productService.getProductById(id).pipe(
      catchError(() => of(null))
    ));

    forkJoin(calls).subscribe(results => {
      results.forEach((p: any) => {
        if (p && typeof p.id === 'number') {
          this.productNames[p.id] = p.name;
        }
      });
      this.cdr.detectChanges();
    });
  }

  triggerConfetti(): void {
    confetti.create(undefined, { resize: true })({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 }
    });
  }

  setStatus(r: ReportModerationDTO, status: 'REPORTED'|'ACCEPTED'|'DENIED') {
    // Do not allow any changes after a report has been DENIED
    if (r.status === 'DENIED' || r.status === status) {
      return;
    }
    this.updatingId = r.id;
    this.reportService.updateReportStatus(r.id, status).subscribe({
      next: (updated) => {
        const idx = this.reports.findIndex(x => x.id === r.id);
        if (idx !== -1) {
          // Replace immutably to ensure view updates
          this.reports = [
            ...this.reports.slice(0, idx),
            updated,
            ...this.reports.slice(idx + 1)
          ];
          this.triggerConfetti();
        }
        this.updatingId = null;
        this.cdr.detectChanges();
      },
      error: (e) => {
        this.updatingId = null;
        this.cdr.detectChanges();
        alert('Failed to update: ' + (e?.error?.error || 'Unknown error'))
      }
    })
  }
}
