// тут все fetch запросы к FASRTAPI
import type { Product, Application, HistoryItem } from '../types';

// Имитация
const MOCK_PRODUCTS: Product[] = [
  { id: 'p1', name: 'Экспресс-кредит', description: 'Быстрые деньги на развитие бизнеса', minAmount: 50000, maxAmount: 1000000, terms: [6, 12, 24] },
  { id: 'p2', name: 'Кредит на оборот', description: 'Для пополнения складских запасов', minAmount: 500000, maxAmount: 5000000, terms: [12, 24, 36] },
  { id: 'p3', name: 'Инвестиционный', description: 'На покупку оборудования или расширение', minAmount: 1000000, maxAmount: 10000000, terms: [24, 36, 60] }
];

let MOCK_APPLICATIONS: Application[] = [
  { 
    id: 'app-1', 
    productId: 'p1', 
    productName: 'Экспресс-кредит', 
    amount: 300000, 
    term: 12, 
    status: 'APPROVED', 
    createdAt: '2023-10-20', 
    businessName: 'ООО "Ромашка"',
    financials: { monthlyRevenue: 500000, monthlyExpenses: 200000, existingLoanPayments: 0 },
    history: [
      { id: 'h1', date: '2023-10-20T10:00:00', previousStatus: null, newStatus: 'DRAFT', reason: 'Заявка создана' },
      { id: 'h2', date: '2023-10-20T10:05:00', previousStatus: 'DRAFT', newStatus: 'APPROVED', reason: 'Автоматическое одобрение по правилам' }
    ]
  },
  { 
    id: 'app-2', 
    productId: 'p2', 
    productName: 'Кредит на оборот', 
    amount: 2000000, 
    term: 24, 
    status: 'SCORING', 
    createdAt: '2023-10-24', 
    businessName: 'ИП Иванов',
    financials: { monthlyRevenue: 1500000, monthlyExpenses: 900000, existingLoanPayments: 50000 },
    history: [
      { id: 'h3', date: '2023-10-24T14:00:00', previousStatus: null, newStatus: 'DRAFT', reason: 'Заявка создана' },
      { id: 'h4', date: '2023-10-24T14:05:00', previousStatus: 'DRAFT', newStatus: 'SCORING', reason: 'Запущена оценка риска' }
    ]
  }
];

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  // GET /api/products
  getProducts: async (): Promise<Product[]> => {
    await delay(500);
    return [...MOCK_PRODUCTS];
  },

  // GET /api/applications
  getApplications: async (): Promise<Application[]> => {
    await delay(500);
    return [...MOCK_APPLICATIONS];
  },

  // GET /api/applications/{id}
  getApplicationById: async (id: string): Promise<Application | null> => {
    await delay(500);
    const app = MOCK_APPLICATIONS.find(a => a.id === id);
    return app ? { ...app } : null;
  },

  // POST /api/applications
  createApplication: async (data: { 
    productId: string, 
    amount: number, 
    term: number,
    financials: { monthlyRevenue: number, monthlyExpenses: number, existingLoanPayments: number }
  }): Promise<Application> => {
    await delay(800);
    const product = MOCK_PRODUCTS.find(p => p.id === data.productId);
    
    const initialHistory: HistoryItem = {
      id: `h-${Date.now()}`,
      date: new Date().toISOString(),
      previousStatus: null,
      newStatus: 'DRAFT',
      reason: 'Заявка создана и сохранена как черновик'
    };

    const newApp: Application = {
      id: `app-${Date.now()}`,
      productId: data.productId,
      productName: product ? product.name : 'Неизвестный продукт',
      amount: data.amount,
      term: data.term,
      status: 'DRAFT',
      createdAt: new Date().toISOString().split('T')[0],
      businessName: 'Мой Бизнес',
      financials: data.financials,
      history: [initialHistory]
    };

    MOCK_APPLICATIONS = [newApp, ...MOCK_APPLICATIONS];
    return newApp;
  }
};