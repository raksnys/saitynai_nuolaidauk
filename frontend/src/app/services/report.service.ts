import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ReportCreateDTO {
  product?: number;
  discount?: number;
  product_reason?: 'name' | 'photo' | 'price' | null;
  discount_image_base64?: string;
  description: string;
}

export interface ReportModerationDTO {
  id: number;
  product: number | null;
  discount: number | null;
  product_reason: 'name' | 'photo' | 'price' | null;
  discount_image_base64: string;
  description: string;
  status: 'REPORTED' | 'ACCEPTED' | 'DENIED';
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class ReportService {
  private baseUrl = `${environment.apiUrl}/catalog`;

  constructor(private http: HttpClient) {}

  createReport(body: ReportCreateDTO): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/`, body);
  }

  listReports(): Observable<ReportModerationDTO[]> {
    return this.http.get<ReportModerationDTO[]>(`${this.baseUrl}/reports/moderation/`);
  }

  getReport(id: number): Observable<ReportModerationDTO> {
    return this.http.get<ReportModerationDTO>(`${this.baseUrl}/reports/moderation/${id}/`);
  }

  updateReportStatus(id: number, status: 'REPORTED' | 'ACCEPTED' | 'DENIED'): Observable<ReportModerationDTO> {
    return this.http.patch<ReportModerationDTO>(`${this.baseUrl}/reports/moderation/${id}/`, { status });
  }
}
