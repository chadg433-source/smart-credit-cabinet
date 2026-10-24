// тут TypeScript-интерфейсы (Product, Application, HistoryItem)
export type ApplicationStatus = 
  | 'DRAFT' 
  | 'SUBMITTED' 
  | 'DATA_CHECK' 
  | 'MORE_INFO_REQUIRED' 
  | 'EXTERNAL_CHECK' 
  | 'SCORING' 
  | 'DECISION' 
  | 'APPROVED' 
  | 'DECLINED' 
  | 'ALTERNATIVE_OFFER';

export interface Product {
  id: string;
  name: string;
  description: string;
  minAmount: number;
  maxAmount: number;
  terms: number[]; 
}

export type CreditProduct = Product;

export interface HistoryItem {
  id: string;
  date: string; 
  previousStatus: ApplicationStatus | null; 
  newStatus: ApplicationStatus; 
  reason?: string; 
}

export interface Application {
  id: string;
  productId: string;
  productName: string;
  amount: number;
  term: number;
  status: ApplicationStatus;
  createdAt: string;
  businessName: string;

  financials?: {
    monthlyRevenue: number;      
    monthlyExpenses: number;      
    existingLoanPayments: number;
  };

  history?: HistoryItem[];
}