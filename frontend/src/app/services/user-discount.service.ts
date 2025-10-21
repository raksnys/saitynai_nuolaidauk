import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface CreateUserDiscountPayload {
  name: string;
  description?: string;
  discount_type: 'percentage' | 'fixed';
  value: string | number;
  starts_at: string; // ISO string
  ends_at: string;   // ISO string
  store_id: number;
  brand_id?: number;
  all_products?: boolean; // true for store-wide
  category_id?: number;   // for category in store
  product_id?: number;    // for specific product in store
}

@Injectable({ providedIn: 'root' })
export class UserDiscountService {
  private baseUrl = `${environment.apiUrl}/catalog/user/discounts/`;

  constructor(private http: HttpClient) {}

  create(payload: CreateUserDiscountPayload): Observable<any> {
    return this.http.post<any>(this.baseUrl, payload, { withCredentials: true });
  }
}
