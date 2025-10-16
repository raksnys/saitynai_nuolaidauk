export interface Product {
    id: number;
    name: string;
    price: number;
    price_unit: string;
    photo_url: string;
    weight: number;
    description: string;
    category: number;
    brand: number;
    store: number;
    discounts: any[];
    discount_price?: number;
}
