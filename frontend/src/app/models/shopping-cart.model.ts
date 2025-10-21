export interface ShoppingCartItemDiscount {
  id: number;
  name: string;
  discount_type: 'percentage' | 'fixed';
  value: string; // decimal as string from API
  starts_at: string;
  ends_at: string;
}

export interface ShoppingCartItem {
  id: number;
  product: number;
  name: string;
  price: number;
  current_discount: ShoppingCartItemDiscount | null;
  quantity: number;
  is_purchased: boolean;
  brand: number | null;
  brand_name: string | null;
}

export interface ShoppingCart {
  id: number;
  name: string | null;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  updated_at: string;
  items: ShoppingCartItem[];
}