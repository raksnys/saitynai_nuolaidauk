import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-stores',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stores.html',
  styleUrls: ['./stores.css']
})
export class Stores implements OnInit {
  brands: any[] = [];
  private apiUrl = environment.apiUrl;
  sortOrder: string = 'name';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    this.http.get<any[]>(`${this.apiUrl}/catalog/brands/`, { withCredentials: true }).subscribe({
      next: (response) => {
        this.brands = response;
        this.sortBrands();
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Failed to get brands', error);
      }
    });
  }

  sortBrands(): void {
    this.brands.sort((a, b) => {
      if (this.sortOrder === 'name') {
        return a.name.localeCompare(b.name);
      } else if (this.sortOrder === 'stores_count') {
        return b.stores_count - a.stores_count;
      } else if (this.sortOrder === 'products_count') {
        return b.products_count - a.products_count;
      } else if (this.sortOrder === 'active_discounts_count') {
        return b.active_discounts_count - a.active_discounts_count;
      }
      return 0;
    });
  }

  onSortChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    this.sortOrder = selectElement.value;
    this.sortBrands();
  }
}
