import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface WishlistItemDTO {
  id: number;
  product: number;
  product_name: string;
  product_photo_url: string;
  price: string | number;
  discounted_price?: string | number | null;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class WishlistService {
  private baseUrl = `${environment.apiUrl}/catalog/user/wishlist/`;

  constructor(private http: HttpClient) {}

  getWishlist(): Observable<WishlistItemDTO[]> {
    return this.http.get<WishlistItemDTO[]>(this.baseUrl, { withCredentials: true });
  }

  add(productId: number): Observable<WishlistItemDTO> {
    return this.http.post<WishlistItemDTO>(this.baseUrl, { product: productId }, { withCredentials: true });
  }

  remove(productId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${productId}/`, { withCredentials: true });
  }
}
