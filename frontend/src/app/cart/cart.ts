import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ShoppingCart, ShoppingCartItem } from '../models/shopping-cart.model';
import { ShoppingCartService } from '../services/shopping-cart.service';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, CurrencyPipe, DatePipe],
  templateUrl: './cart.html',
  styleUrls: ['./cart.css']
})
export class CartComponent implements OnInit {
  openCart: ShoppingCart | null = null;
  history: ShoppingCart[] = [];
  newCartName = '';
  isLoading = true;
  error: string | null = null;
  
  // Grouped view of items by brand within the open cart
  get groupedOpenItems(): { brand_name: string | null; brand: number | null; items: ShoppingCartItem[] }[] {
    if (!this.openCart) return [];
    const groups = new Map<string, { brand_name: string | null; brand: number | null; items: ShoppingCartItem[] }>();
    for (const it of this.openCart.items) {
      const key = String(it.brand ?? 'null');
      if (!groups.has(key)) {
        groups.set(key, { brand_name: it.brand_name ?? 'Other', brand: it.brand ?? null, items: [] });
      }
      groups.get(key)!.items.push(it);
    }
    return Array.from(groups.values());
  }

  groupCartItems(c: ShoppingCart): { brand_name: string | null; brand: number | null; items: ShoppingCartItem[] }[] {
    const groups = new Map<string, { brand_name: string | null; brand: number | null; items: ShoppingCartItem[] }>();
    for (const it of (c.items || [])) {
      const key = String(it.brand ?? 'null');
      if (!groups.has(key)) {
        groups.set(key, { brand_name: it.brand_name ?? 'Other', brand: it.brand ?? null, items: [] });
      }
      groups.get(key)!.items.push(it);
    }
    return Array.from(groups.values());
  }

  constructor(
    private cartService: ShoppingCartService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.isLoading = true;
    this.error = null;
    this.cdr.detectChanges();
    this.cartService.getOpenCart().subscribe({
      next: cart => {
        this.openCart = cart;
        this.loadHistory();
      },
      error: err => {
        console.error(err);
        this.error = 'Failed to load your cart.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  private loadHistory(): void {
    this.cartService.list('CLOSED').subscribe({
      next: hist => {
        this.history = hist;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  createCart(): void {
    this.cartService.create(this.newCartName || undefined).subscribe({
      next: cart => { this.openCart = cart; this.newCartName = ''; this.cdr.detectChanges(); },
      error: err => { this.error = err?.error?.detail || 'Could not create cart.'; this.cdr.detectChanges(); }
    });
  }

  inc(item: ShoppingCartItem): void {
    if (!this.openCart) return;
    this.cartService.addItem(this.openCart.id, item.product, item.quantity + 1).subscribe({
      next: cart => { this.openCart = cart; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  dec(item: ShoppingCartItem): void {
    if (!this.openCart) return;
    const q = Math.max(1, item.quantity - 1);
    this.cartService.updateItem(this.openCart.id, { product: item.product, quantity: q }).subscribe({
      next: cart => { this.openCart = cart; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  togglePurchased(item: ShoppingCartItem): void {
    if (!this.openCart) return;
    this.cartService.updateItem(this.openCart.id, { product: item.product, is_purchased: !item.is_purchased }).subscribe({
      next: cart => { this.openCart = cart; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  remove(item: ShoppingCartItem): void {
    if (!this.openCart) return;
    this.cartService.removeItem(this.openCart.id, item.product).subscribe({
      next: cart => { this.openCart = cart; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  closeCart(): void {
    if (!this.openCart) return;
    this.cartService.close(this.openCart.id).subscribe({
      next: cart => { this.openCart = cart; this.refresh(); },
      error: () => {}
    });
  }

  getItemDiscountedPrice(item: ShoppingCartItem): number {
    if (!item.current_discount) return item.price;
    const v = parseFloat(item.current_discount.value);
    if (item.current_discount.discount_type === 'percentage') {
      return Math.max(0, +(item.price * (1 - v / 100)).toFixed(2));
    }
    return Math.max(0, +(item.price - v).toFixed(2));
  }
}
