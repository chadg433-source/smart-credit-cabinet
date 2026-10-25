// src/types/index.ts
export interface CreditProduct {
  id: string;
  name: string;
  description: string;
  min_amount: number;
  max_amount: number;
  min_term_months: number;
  max_term_months: number;
  annual_rate: number;
}

export interface Application {
  id: string;
  business_id: string;
  credit_product_id: string;
  requested_amount: number;
  requested_term_months: number;
  status: string;
  purpose: string;
}

export interface HistoryItem {
  old_status: string;
  new_status: string;
  comment: string;
  created_at: string;
}