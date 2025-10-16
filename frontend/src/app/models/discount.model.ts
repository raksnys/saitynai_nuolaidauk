export interface Discount {
    id: number;
    name: string;
    description: string;
    discount_type: 'percentage' | 'absolute';
    value: number;
    starts_at: string;
    ends_at: string;
    status: string;
    target_type: 'product' | 'category' | 'brand';
    product: number;
    category: number;
    brand: number;
    submitted_by: number;
    created_at: string;
    updated_at: string;
    effective_status: string;
}
