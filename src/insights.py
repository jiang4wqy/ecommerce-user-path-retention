from __future__ import annotations

import pandas as pd


def generate_insights(outputs: dict[str, pd.DataFrame]) -> list[str]:
    daily = outputs["daily_kpis"]
    funnel = outputs["funnel"]
    segments = outputs["segments"]
    category = outputs["category"]
    cart_abandonment = outputs.get("cart_abandonment")
    price_band = outputs.get("price_band")

    insights: list[str] = []
    if not funnel.empty:
        view_users = _step_users(funnel, "view")
        cart_users = _step_users(funnel, "cart")
        purchase_users = _step_users(funnel, "purchase")
        cart_drop = 1 - (cart_users / view_users if view_users else 0)
        purchase_drop = 1 - (purchase_users / cart_users if cart_users else 0)
        insights.append(
            f"浏览到加购流失率约 {cart_drop:.1%}，加购到购买流失率约 {purchase_drop:.1%}；优先优化加购召回和价格/优惠提醒。"
        )

    if not daily.empty:
        avg_purchase_rate = daily["purchase_rate"].mean()
        insights.append(
            f"样本期平均浏览购买转化率约 {avg_purchase_rate:.2%}，适合用首页推荐、商品详情页信任信息和购物车触达提升转化。"
        )

    if not segments.empty:
        top_segment = segments.iloc[0]
        insights.append(
            f"最大用户群体是 {top_segment['segment']}，占比 {top_segment['share']:.1%}；运营策略应先覆盖最大流量池。"
        )

    if not category.empty:
        best = category.iloc[0]
        insights.append(
            f"收入贡献最高品类是 {best['category_code']}，GMV 约 {best['gmv']:.0f}；可作为推荐位和活动资源倾斜对象。"
        )

    if cart_abandonment is not None and not cart_abandonment.empty:
        abandon = cart_abandonment.iloc[0]
        insights.append(
            f"加购未买用户约 {int(abandon['cart_without_purchase_users'])} 人，加购放弃率约 {abandon['abandonment_rate']:.1%}；适合做购物车召回和价格提醒。"
        )

    if price_band is not None and not price_band.empty:
        top_band = price_band.sort_values("purchase_rate", ascending=False).iloc[0]
        insights.append(
            f"购买转化率最高价格带是 {top_band['price_band']}，转化率约 {top_band['purchase_rate']:.2%}；可作为定价和推荐策略参考。"
        )

    insights.append(
        "项目重点不是预测模型，而是把用户行为日志转化为指标、诊断和可执行的产品运营建议。"
    )
    return insights


def _step_users(funnel: pd.DataFrame, step: str) -> int:
    rows = funnel.loc[funnel["step"] == step, "users"]
    return int(rows.iloc[0]) if not rows.empty else 0
