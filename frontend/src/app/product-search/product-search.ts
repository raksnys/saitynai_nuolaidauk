import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Product } from '../models/product.model';
import { ProductService } from '../services/product.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-product-search',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-search.html',
  styleUrls: ['./product-search.css']
})
export class ProductSearchComponent implements OnInit {
  products: Product[] = [];
  loading = true;
  error: string | null = null;
  query = '';

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.query = params.get('q') || '';
      if (this.query) {
        this.searchProducts();
      } else {
        this.products = [];
        this.loading = false;
      }
    });
  }

  searchProducts(): void {
    this.loading = true;
    this.error = null;
    this.productService.searchProducts(this.query).subscribe({
      next: (data) => {
        this.products = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (e) => {
        this.error = 'Failed to perform search. Please try again.';
        this.loading = false;
        console.error(e);
        this.cdr.detectChanges();
      }
    });
  }
}
