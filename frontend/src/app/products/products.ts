import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './products.html',
  styleUrls: ['./products.css']
})
export class Products implements OnInit {
  products: any[] = [];
  brands: any[] = [];
  categories: any[] = [];
  currentPage = 1;
  totalPages = 1;
  isLoading = true;
  error: string | null = null;
  
  filters: {
    min_price: number | null;
    max_price: number | null;
    brand: string;
    category: string;
    ordering: string;
  } = {
    min_price: null,
    max_price: null,
    brand: '',
    category: '',
    ordering: ''
  };

  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    this.loadProducts();
    this.loadBrands();
    this.loadCategories();
  }

  loadProducts(page: number = 1): void {
    this.isLoading = true;
    this.error = null;
    this.cdr.detectChanges();

    let params = new HttpParams().set('page', page.toString());

    if (this.filters.min_price) {
      params = params.set('min_price', this.filters.min_price.toString());
    }
    if (this.filters.max_price) {
      params = params.set('max_price', this.filters.max_price.toString());
    }
    if (this.filters.brand) {
      params = params.set('brand', this.filters.brand);
    }
    if (this.filters.category) {
      params = params.set('category', this.filters.category);
    }
    if (this.filters.ordering) {
      params = params.set('ordering', this.filters.ordering);
    }

    this.http.get<any>(`${this.apiUrl}/catalog/products/`, { params, withCredentials: true }).subscribe({
      next: (response) => {
        this.products = response.results;
        this.currentPage = response.current_page;
        this.totalPages = response.total_pages;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Failed to get products', error);
        this.error = 'Failed to load products. Please make sure the backend is running.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  loadBrands(): void {
    this.http.get<any[]>(`${this.apiUrl}/catalog/brands/`, { withCredentials: true }).subscribe(data => {
      this.brands = data;
    });
  }

  loadCategories(): void {
    this.http.get<any[]>(`${this.apiUrl}/catalog/categories/`, { withCredentials: true }).subscribe(data => {
      this.categories = data;
    });
  }

  applyFilters(): void {
    this.loadProducts();
  }

  resetFilters(): void {
    this.filters = {
      min_price: null,
      max_price: null,
      brand: '',
      category: '',
      ordering: ''
    };
    this.loadProducts();
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.loadProducts(this.currentPage + 1);
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.loadProducts(this.currentPage - 1);
    }
  }
}
