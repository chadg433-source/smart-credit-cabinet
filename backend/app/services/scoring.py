from decimal import Decimal
from app.models import Business, CreditProduct

def calculate_scoring(business: Business, product: CreditProduct, requested_amount: Decimal) -> dict:

    score = 50

    monthly_profit = business.monthly_revenue - business.monthly_expenses
    if monthly_profit > 300_000:
        score += 20
    elif monthly_profit > 100_000:
        score += 10
    else:
        score -= 10

    if business.monthly_revenue > 0:
        debt_ratio = business.existing_monthly_loan_payments / business.monthly_revenue
        if debt_ratio < 0.3:
            score += 15
        elif debt_ratio > 0.5:
            score -= 20

    if requested_amount > business.monthly_revenue * 10:
        score -= 15
    else:
        score += 5

    if product and requested_amount > product.max_amount:
        score -= 20

    score = max(0, min(100, score))

    if score >= 70:
        decision = "APPROVED"
        reason = "Высокая платежеспособность"
        offered_amount = requested_amount
    elif score >= 50:
        decision = "APPROVED_WITH_CONDITIONS"
        reason = "Средняя платежеспособность. Сумма снижена."
        offered_amount = requested_amount * Decimal("0.7")
    else:
        decision = "REJECTED"
        reason = "Высокий риск"
        offered_amount = Decimal("0.00")

    return {
        "total_score": Decimal(str(score)),
        "decision": decision,
        "reason": reason,
        "offered_amount": offered_amount
    }