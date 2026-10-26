
import type {
  CreditProduct,
  Application,
  ApplicationUpdate,
  HistoryItem,
  Business,
} from '../types';

const API_URL = 'http://localhost:8000';
const TOKEN_KEY = 'access_token';

type TokenResponse = {
  access_token: string;
  token_type: string;
};

type Entrepreneur = {
  id: string;
  full_name: string;
  created_at: string;
};

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers = new Headers(options.headers);

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    throw new Error('Сессия истекла. Войдите снова.');
  }

  if (!res.ok) {
    throw new Error(`Ошибка API: ${res.status}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export const api = {
  // POST /auth/demo-login
  demoLogin: async (): Promise<TokenResponse> => {
    const result = await request<TokenResponse>('/auth/demo-login', {
      method: 'POST',
    });

    localStorage.setItem(TOKEN_KEY, result.access_token);

    return result;
  },

  // GET /auth/me
  getMe: (): Promise<Entrepreneur> =>
    request<Entrepreneur>('/auth/me'),

  // GET /products/
  getProducts: (): Promise<CreditProduct[]> =>
    request<CreditProduct[]>('/products/'),

  // GET /businesses/
  getBusinesses: (): Promise<Business[]> =>
    request<Business[]>('/businesses/'),

  // GET /applications/
  getApplications: (): Promise<Application[]> =>
    request<Application[]>('/applications/'),

  // GET /applications/{id}
  getApplicationById: async (
    id: string,
  ): Promise<Application | null> => {
    try {
      return await request<Application>(`/applications/${id}`);
    } catch {
      return null;
    }
  },

  // POST /applications/
  createApplication: (data: {
    business_id: string;
    credit_product_id: string;
    requested_amount: number;
    requested_term_months: number;
    purpose: string;
  }): Promise<Application> =>
    request<Application>('/applications/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // PATCH /applications/{id}
  updateApplication: (
    id: string,
    data: ApplicationUpdate,
  ): Promise<Application> =>
    request<Application>(`/applications/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // POST /applications/{id}/submit
  submitApplication: (id: string): Promise<Application> =>
    request<Application>(`/applications/${id}/submit`, {
      method: 'POST',
    }),

  // GET /applications/{id}/history
  getHistory: (id: string): Promise<HistoryItem[]> =>
    request<HistoryItem[]>(`/applications/${id}/history`),

  // POST /applications/{id}/process
  processApplication: (id: string): Promise<Application> =>
    request<Application>(`/applications/${id}/process`, {
      method: 'POST',
    }),

  // GET /applications/bank/queue
  getBankQueue: (): Promise<unknown[]> =>
    request<unknown[]>('/applications/bank/queue'),
};
