# Модель данных (ER)

СУБД: PostgreSQL 16. ORM: SQLAlchemy. Все ID — UUID. Денежные суммы — `NUMERIC(15,2)`, баллы и ставки — `NUMERIC(5,2)`.

```mermaid
erDiagram
    ENTREPRENEURS ||--o{ BUSINESSES : "владеет"
    BUSINESSES ||--o{ APPLICATIONS : "подаёт"
    CREDIT_PRODUCTS ||--o{ APPLICATIONS : "запрошен"
    APPLICATIONS ||--o{ EXTERNAL_CHECK_RESULTS : "внешние проверки"
    APPLICATIONS ||--o{ SCORING_RESULTS : "скоринг"
    APPLICATIONS ||--o{ CREDIT_DECISIONS : "решение"
    APPLICATIONS ||--o{ APPLICATION_STATUS_HISTORY : "история статусов"

    ENTREPRENEURS {
        uuid id PK
        string full_name
        datetime created_at
    }
    BUSINESSES {
        uuid id PK
        uuid entrepreneur_id FK
        string name
        string tax_id UK
        string business_type
        date registration_date
        numeric monthly_revenue
        numeric monthly_expenses
        numeric existing_monthly_loan_payments
        datetime updated_at
    }
    CREDIT_PRODUCTS {
        uuid id PK
        string name
        text description
        numeric min_amount
        numeric max_amount
        int min_term_months
        int max_term_months
        numeric annual_rate
        bool is_active
    }
    APPLICATIONS {
        uuid id PK
        uuid business_id FK
        uuid credit_product_id FK
        numeric requested_amount
        int requested_term_months
        string purpose
        string status
        datetime created_at
        datetime updated_at
    }
    EXTERNAL_CHECK_RESULTS {
        uuid id PK
        uuid application_id FK
        string check_type
        string status
        text result_data
        datetime checked_at
    }
    SCORING_RESULTS {
        uuid id PK
        uuid application_id FK
        numeric total_score
        numeric financial_stability_score
        numeric payment_capacity_score
        numeric business_age_score
        numeric external_checks_score
        text input_snapshot
        datetime created_at
    }
    CREDIT_DECISIONS {
        uuid id PK
        uuid application_id FK
        string decision
        text reason
        numeric offered_amount
        int offered_term_months
        numeric offered_rate
        datetime created_at
    }
    APPLICATION_STATUS_HISTORY {
        uuid id PK
        uuid application_id FK
        string old_status
        string new_status
        datetime changed_at
        text comment
    }
```

## Описание сущностей
- **`entrepreneurs`**: Предприниматель (ФИО).
- **`businesses`**: Бизнес (ИНН, выручка, расходы, текущие платежи). Связан с предпринимателем.
- **`credit_products`**: Каталог продуктов с валидацией диапазонов сумм и сроков (CHECK constraints).
- **`applications`**: Ядро системы. Хранит параметры заявки и текущий статус. Связана с продуктом и бизнесом (используются `relationship` для подгрузки имени продукта).
- **`application_status_history`**: Аудит переходов статусов (заполняется автоматически при смене статуса).
- **`scoring_results`** и **`credit_decisions`**: Разделяют оценку риска и итоговое решение банка.