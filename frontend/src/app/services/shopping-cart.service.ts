import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../environments/environment';
import { ShoppingCart, ShoppingCartItem } from '../models/shopping-cart.model';

@Injectable({ providedIn: 'root' })
export class ShoppingCartService {
  private baseUrl = `${environment.apiUrl}/catalog/shopping-carts/`;

  constructor(private http: HttpClient) {}

  list(status?: 'OPEN' | 'CLOSED'): Observable<ShoppingCart[]> {
    const url = status ? `${this.baseUrl}?status=${status}` : this.baseUrl;
    return this.http.get<ShoppingCart[]>(url, { withCredentials: true });
  }

  getOpenCart(): Observable<ShoppingCart | null> {
    return this.list('OPEN').pipe(map(carts => carts.length ? carts[0] : null));
  }

  create(name?: string): Observable<ShoppingCart> {
    const body: any = {};
    if (name) body.name = name;
    return this.http.post<ShoppingCart>(this.baseUrl, body, { withCredentials: true });
  }

  addItem(cartId: number, product: number, quantity = 1, increment = false): Observable<ShoppingCart> {
    const body: any = { product, quantity };
    if (increment) body.increment = true;
    return this.http.post<ShoppingCart>(`${this.baseUrl}${cartId}/add-item/`, body, { withCredentials: true });
  }

  updateItem(cartId: number, update: Partial<Pick<ShoppingCartItem, 'product' | 'quantity' | 'is_purchased'>>): Observable<ShoppingCart> {
    return this.http.patch<ShoppingCart>(`${this.baseUrl}${cartId}/update-item/`, update, { withCredentials: true });
  }

  removeItem(cartId: number, product: number): Observable<ShoppingCart> {
    return this.http.delete<ShoppingCart>(`${this.baseUrl}${cartId}/remove-item/?product=${product}`, { withCredentials: true });
  }

  close(cartId: number): Observable<ShoppingCart> {
    return this.http.post<ShoppingCart>(`${this.baseUrl}${cartId}/close/`, {}, { withCredentials: true });
  }
}