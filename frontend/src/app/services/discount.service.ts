import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProductDiscountHistory } from '../models/product-discount-history.model';
import { environment } from '../../environments/environment';
import { Discount } from '../models/discount.model';

@Injectable({
  providedIn: 'root'
})
export class DiscountService {
  private discountApiUrl = `${environment.apiUrl}/catalog/discounts/`;
  private discountHistoryApiUrl = `${environment.apiUrl}/catalog/product-discount-history/`;

  constructor(private http: HttpClient) { }

  getDiscounts(): Observable<Discount[]> {
    return this.http.get<Discount[]>(this.discountApiUrl);
  }

  getDiscountHistoryForProduct(productId: number): Observable<ProductDiscountHistory[]> {
    return this.http.get<ProductDiscountHistory[]>(`${this.discountHistoryApiUrl}?product=${productId}`);
  }
}
