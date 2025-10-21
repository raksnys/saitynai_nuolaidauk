import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { UserDiscountService } from '../services/user-discount.service';

@Component({
  selector: 'app-discount-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './discount-create.html',
  styleUrls: ['./discount-create.css']
})
export class DiscountCreateComponent {
  brands: any[] = [];
  stores: any[] = [];
  filteredStores: any[] = [];
  categories: any[] = [];
  productResults: any[] = [];

  // Form state
  brandId: number | null = null;
  storeId: number | null = null;
  scope: 'all' | 'category' | 'product' = 'all';
  categoryId: number | null = null;
  productId: number | null = null;
  productQuery = '';
  name = '';
  description = '';
  discountType: 'percentage' | 'fixed' = 'percentage';
  value: number | null = null;
  startsAt = ''; // datetime-local
  endsAt = '';

  isSubmitting = false;
  submittedId: number | null = null;
  error: string | null = null;

  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private service: UserDiscountService,
    private cdr: ChangeDetectorRef,
  ) {
    this.loadBrands();
    this.loadStores();
    this.loadCategories();
  }

  loadBrands(): void {
    this.http.get<any[]>(`${this.apiUrl}/catalog/brands/`, { withCredentials: true }).subscribe({
      next: (data) => { this.brands = data; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  loadStores(): void {
    this.http.get<any[]>(`${this.apiUrl}/catalog/stores/`, { withCredentials: true }).subscribe({
      next: (data) => { this.stores = data; this.filterStores(); this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  loadCategories(): void {
    this.http.get<any[]>(`${this.apiUrl}/catalog/categories/`, { withCredentials: true }).subscribe({
      next: (data) => { this.categories = data; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  filterStores(): void {
    if (!this.brandId) { this.filteredStores = this.stores; return; }
    this.filteredStores = this.stores.filter(s => s.brand === this.brandId);
    if (this.storeId && !this.filteredStores.some(s => s.id === this.storeId)) {
      this.storeId = null;
    }
  }

  onBrandChange(): void {
    this.filterStores();
  }

  searchProducts(): void {
    if (!this.productQuery.trim()) { this.productResults = []; return; }
    const params = new HttpParams().set('q', this.productQuery.trim());
    this.http.get<any[]>(`${this.apiUrl}/catalog/products/search`, { params, withCredentials: true }).subscribe({
      next: (res) => { this.productResults = res; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  pickProduct(p: any): void {
    this.productId = p.id;
    this.productQuery = p.name;
    this.productResults = [];
    // Auto-select brand/store if not chosen (best effort)
    if (!this.brandId && p.brand) this.brandId = p.brand;
    if (!this.storeId && p.store) this.storeId = p.store;
    this.filterStores();
  }

  private toIso(dtLocal: string): string {
    // datetime-local -> ISO
    try { return new Date(dtLocal).toISOString(); } catch { return dtLocal; }
  }

  canSubmit(): boolean {
    if (!this.name || !this.value || !this.startsAt || !this.endsAt || !this.storeId) return false;
    if (this.scope === 'category' && !this.categoryId) return false;
    if (this.scope === 'product' && !this.productId) return false;
    return true;
  }

  submit(): void {
    if (!this.canSubmit()) return;
    this.isSubmitting = true;
    this.error = null;
    const payload: any = {
      name: this.name,
      description: this.description || undefined,
      discount_type: this.discountType,
      value: String(this.value),
      starts_at: this.toIso(this.startsAt),
      ends_at: this.toIso(this.endsAt),
      store_id: this.storeId!,
      brand_id: this.brandId || undefined,
    };

    if (this.scope === 'all') {
      payload.all_products = true;
    } else if (this.scope === 'category') {
      payload.category_id = this.categoryId;
    } else if (this.scope === 'product') {
      payload.product_id = this.productId;
    }

    this.service.create(payload).subscribe({
      next: (res) => {
        this.submittedId = res?.id ?? null;
        this.isSubmitting = false;
        this.cdr.detectChanges();
      },
      error: (e) => {
        this.error = e?.error?.detail || 'Failed to submit discount. Please check your inputs.';
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }
    });
  }
}
