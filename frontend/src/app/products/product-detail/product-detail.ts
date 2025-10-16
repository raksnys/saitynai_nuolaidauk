import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { switchMap, forkJoin, of, catchError } from 'rxjs';
import { Product } from '../../models/product.model';
import { Brand } from '../../models/brand.model';
import { ProductDiscountHistory } from '../../models/product-discount-history.model';
import { ProductService } from '../../services/product.service';
import { BrandService } from '../../services/brand.service';
import { DiscountService } from '../../services/discount.service';
import { CurrencyPipe, DatePipe, CommonModule } from '@angular/common';
import { WishlistService, WishlistItemDTO } from '../../services/wishlist.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, CommonModule],
  templateUrl: './product-detail.html',
  styleUrls: ['./product-detail.css']
})
export class ProductDetailComponent implements OnInit {
  product: Product | undefined;
  brand: Brand | undefined;
  discountHistory: ProductDiscountHistory[] = [];
  relatedProducts: Product[] = [];
  isModalOpen = false;
  isLoading = true;
  error: string | null = null;
  isWishlisted = false;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private brandService: BrandService,
    private discountService: DiscountService,
    private wishlistService: WishlistService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.paramMap.pipe(
      switchMap(params => {
        const productId = params.get('id');
        if (productId) {
          // When the route changes, reset the state
          this.product = undefined;
          this.relatedProducts = [];
          this.isLoading = true;
          this.error = null;
          
          return this.productService.getProductById(+productId).pipe(
            switchMap((product: Product) => {
              this.product = product;
              
              // Fetch brand, discount history, and all products for related products section
              // Add catchError to each observable so one failure doesn't break the whole chain
              const brand$ = this.brandService.getBrandById(product.brand).pipe(
                catchError(err => {
                  console.warn('Failed to load brand:', err);
                  return of(undefined);
                })
              );
              
              const discountHistory$ = this.discountService.getDiscountHistoryForProduct(product.id).pipe(
                catchError(err => {
                  console.warn('Failed to load discount history:', err);
                  return of([]);
                })
              );
              
              const allProducts$ = this.productService.getProducts().pipe(
                catchError(err => {
                  console.warn('Failed to load all products:', err);
                  return of({ results: [] } as any);
                })
              );

              const wishlist$ = this.wishlistService.getWishlist().pipe(
                catchError(err => {
                  console.warn('Failed to load wishlist:', err);
                  return of([] as WishlistItemDTO[]);
                })
              );

              return forkJoin({ 
                brand: brand$, 
                discountHistory: discountHistory$,
                allProducts: allProducts$,
                wishlist: wishlist$
              });
            }),
            catchError(err => {
              console.error('Error loading product:', err);
              this.error = 'Failed to load product. Please check if the backend is running at http://localhost:8002';
              this.isLoading = false;
              this.cdr.detectChanges();
              return of(null);
            })
          );
        }
        return of(null);
      })
    ).subscribe({
      next: (data) => {
        if (data && this.product) {
          this.brand = data.brand;
          this.discountHistory = data.discountHistory;
          this.isWishlisted = (data.wishlist as WishlistItemDTO[]).some(w => w.product === this.product!.id);

          // Filter for related products
          this.relatedProducts = (data.allProducts?.results || [])
            .filter((p: Product) => p.category === this.product?.category && p.id !== this.product?.id)
            .slice(0, 3);
        }
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading product details:', err);
        this.error = 'Failed to load product details. Please try again.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  navigateToProduct(productId: number): void {
    this.router.navigate(['/products', productId]);
  }

  toggleWishlist(): void {
    if (!this.product) return;
    if (this.isWishlisted) {
      this.wishlistService.remove(this.product.id).subscribe({
        next: () => {
          this.isWishlisted = false;
          this.cdr.detectChanges();
        },
        error: (e) => console.error('Failed to remove from wishlist', e)
      });
    } else {
      this.wishlistService.add(this.product.id).subscribe({
        next: () => {
          this.isWishlisted = true;
          this.cdr.detectChanges();
        },
        error: (e) => console.error('Failed to add to wishlist', e)
      });
    }
  }
}
