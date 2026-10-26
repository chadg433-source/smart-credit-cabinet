
export const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Черновик",
  SUBMITTED: "Отправлена в банк",
  VALIDATION: "Проверка данных",
  EXTERNAL_CHECKS: "Внешние проверки (БКИ, ЕГРЮЛ)",
  SCORING: "Оценка рисков",
  DECISION_PENDING: "Принятие решения",
  APPROVED: "Одобрено",
  APPROVED_WITH_CONDITIONS: "Одобрено на условиях",
  REJECTED: "Отказ",
  NEED_MORE_INFO: "Нужны документы",
  DOCUMENTS: "Подписание документов",
  DISBURSED: "Деньги выданы",
};

export const getStatusLabel = (status: string): string => {
  return STATUS_LABELS[status] || status;
};