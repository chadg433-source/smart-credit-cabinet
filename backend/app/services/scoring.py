from decimal import Decimal
from app.models import Business, CreditProduct

def calculate_scoring(business: Business, product: CreditProduct, requested_amount: Decimal) -> dict:
    zero = Decimal("0")
    hundred = Decimal("100")

    monthly_profit = business.monthly_revenue - business.monthly_expenses
    if business.monthly_revenue > zero:
        profitability = (
            monthly_profit / business.monthly_revenue
        ) * hundred
    else:
        profitability = zero

    if profitability <= zero:
        profitability_score = zero
    elif profitability < Decimal("5"):
        profitability_score = Decimal("6") * profitability
    elif profitability < Decimal("15"):
        profitability_score = Decimal("3") * profitability + Decimal("15")
    elif profitability <= Decimal("30"):
        profitability_score = (
            Decimal("8") / Decimal("3") * profitability
            + Decimal("20")
        )
    else:
        profitability_score = hundred

    debt_ratio_score = zero
    if business.monthly_revenue > zero:
        debt_ratio = (
            business.existing_monthly_loan_payments
            / business.monthly_revenue
        ) * hundred

        if debt_ratio <= Decimal("30"):
            debt_ratio_score = (
                Decimal("100")
                - Decimal("4") / Decimal("3") * debt_ratio
            )
        elif debt_ratio < Decimal("50"):
            debt_ratio_score = (
                Decimal("120") - Decimal("2") * debt_ratio
            )
        elif debt_ratio < Decimal("70"):
            debt_ratio_score = (
                Decimal("70") - debt_ratio
            )
        else:
            debt_ratio_score = zero

    score = (profitability_score + debt_ratio_score) / Decimal("2")

    if business.monthly_revenue <= zero:
        score -= Decimal("15")
    elif requested_amount > business.monthly_revenue * Decimal("10"):
        score -= Decimal("15")

    if product and requested_amount > product.max_amount:
        score -= Decimal("20")

    score = max(zero, min(hundred, score))

    if score >= Decimal("70"):
        decision = "APPROVED"
        reason = "Высокая платежеспособность"
        offered_amount = requested_amount
    elif score >= Decimal("50"):
        decision = "APPROVED_WITH_CONDITIONS"
        reason = "Средняя платежеспособность. Сумма снижена."
        offered_amount = requested_amount * Decimal("0.7")
    else:
        decision = "REJECTED"
        reason = "Высокий риск"
        offered_amount = zero

    return {
        "total_score": score.quantize(Decimal("0.01")),
        "decision": decision,
        "reason": reason,
        "offered_amount": offered_amount,
    }
