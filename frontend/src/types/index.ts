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
  product_name: string
  requested_amount: number;
  requested_term_months: number;
  status: ApplicationStatus;
  purpose: string;
  created_at: string

}

export interface HistoryItem {
  old_status: ApplicationStatus;
  new_status: ApplicationStatus;
  comment: string;
  created_at: string;
}

export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'VALIDATION'
  | 'NEED_MORE_INFO'
  | 'EXTERNAL_CHECKS'
  | 'SCORING'
  | 'DECISION_PENDING'
  | 'APPROVED'
  | 'APPROVED_WITH_CONDITIONS'
  | 'REJECTED'
  | 'DOCUMENTS'
  | 'DISBURSED';