// src/api/client.ts
import type { Product, Application, HistoryItem } from '../types';

const API_URL = "http://localhost:8000";

export const api = {
  // GET /products
  getProducts: async (): Promise<Product[]> => {
    const res = await fetch(`${API_URL}/products/`);
    if (!res.ok) throw new Error("Ошибка загрузки продуктов");
    return res.json();
  },

  // GET /applications
  getApplications: async (): Promise<Application[]> => {
    const res = await fetch(`${API_URL}/applications/`);
    if (!res.ok) throw new Error("Ошибка загрузки заявок");
    return res.json();
  },

  // GET /applications/{id}
  getApplicationById: async (id: string): Promise<Application | null> => {
    const res = await fetch(`${API_URL}/applications/${id}`);
    if (!res.ok) return null; // Если 404, возвращаем null, как в старом коде
    return res.json();
  },

  // POST /applications/
  createApplication: async (data: {
    business_id: string;
    credit_product_id: string;
    requested_amount: number;
    requested_term_months: number;
    purpose: string;
  }): Promise<Application> => {
    const res = await fetch(`${API_URL}/applications/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Ошибка создания заявки");
    return res.json();
  },

  // POST /applications/{id}/submit
  submitApplication: async (id: string): Promise<Application> => {
    const res = await fetch(`${API_URL}/applications/${id}/submit`, { method: "POST" });
    if (!res.ok) throw new Error("Ошибка отправки заявки");
    return res.json();
  },

  // GET /applications/{id}/history
  getHistory: async (id: string): Promise<HistoryItem[]> => {
    const res = await fetch(`${API_URL}/applications/${id}/history`);
    if (!res.ok) throw new Error("Ошибка загрузки истории");
    return res.json();
  },

  // POST /applications/{id}/process
  processApplication: async (id: string): Promise<Application> => {
    const res = await fetch(`${API_URL}/applications/${id}/process`, { method: "POST" });
    if (!res.ok) throw new Error("Ошибка обработки заявки");
    return res.json();
  },

  // GET /applications/bank/queue
  getBankQueue: async (): Promise<any[]> => {
    const res = await fetch(`${API_URL}/applications/bank/queue`);
    if (!res.ok) throw new Error("Ошибка загрузки очереди");
    return res.json();
  }
};