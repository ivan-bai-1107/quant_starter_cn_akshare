from __future__ import annotations

from datetime import date

import streamlit as st

from src.backtest_cn import run_backtest as run_stock_backtest
from src.backtest_sector_rotation import run_backtest as run_sector_backtest
from src.report import compute_stats
from src.sector_cn import get_industry_list
from src.utils import normalize_symbol

st.set_page_config(page_title="Quant Starter CN", page_icon="📈", layout="wide")

st.title("📈 A股量化研究可视化界面")
st.caption("支持单只股票回测与行业轮动策略的快速可视化探索。")


def render_nav(nav):
    st.subheader("净值曲线")
    st.line_chart(nav)
    st.write(f"最新净值：{nav.iloc[-1]:.4f}")


def render_stats(nav, returns):
    st.subheader("策略统计")
    stats = compute_stats(nav, returns)
    st.dataframe(stats, use_container_width=True)


tabs = st.tabs(["单只股票回测", "行业轮动回测"])

with tabs[0]:
    st.markdown("#### 参数设置")
    with st.form("stock_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mode = st.selectbox("数据模式", ["online", "offline"], index=0)
        with col2:
            symbol = st.text_input("股票代码", value="600519")
        with col3:
            start = st.date_input("开始日期", value=date(2018, 1, 1))
        with col4:
            end = st.date_input("结束日期", value=date.today())
        adjust = st.selectbox("复权方式", ["qfq", "hfq", ""])
        submit = st.form_submit_button("运行回测")

    if submit:
        with st.spinner("正在运行回测..."):
            nav, returns = run_stock_backtest(
                normalize_symbol(symbol),
                mode,
                start.isoformat() if start else None,
                end.isoformat() if end else None,
                adjust or "qfq",
            )
        col_left, col_right = st.columns([2, 1])
        with col_left:
            render_nav(nav)
        with col_right:
            render_stats(nav, returns)

with tabs[1]:
    st.markdown("#### 参数设置")
    with st.form("sector_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            mode = st.selectbox("数据模式", ["online", "offline"], index=0, key="sector_mode")
        with col2:
            start = st.date_input("开始日期", value=date(2018, 1, 1), key="sector_start")
        with col3:
            end = st.date_input("结束日期", value=date.today(), key="sector_end")

        col4, col5 = st.columns(2)
        with col4:
            top_k = st.number_input("每期选择行业数量", min_value=1, max_value=10, value=3)
        with col5:
            use_trend_filter = st.checkbox("启用趋势过滤", value=False)

        st.markdown("**行业列表**")
        use_all = st.checkbox("自动加载全部行业（在线）", value=True)
        industries = []
        if use_all:
            industries = get_industry_list()
            st.write(f"已加载行业数量：{len(industries)}")
        else:
            industry_text = st.text_area(
                "请输入行业名称（使用空格或换行分隔）",
                value="半导体 银行 医药商业 煤炭 证券",
            )
            industries = [item for item in industry_text.split() if item]

        submit_sector = st.form_submit_button("运行回测")

    if submit_sector:
        if not industries:
            st.warning("请至少提供一个行业名称。")
        else:
            with st.spinner("正在运行行业轮动回测..."):
                nav, returns, selected = run_sector_backtest(
                    mode,
                    industries,
                    start.isoformat() if start else None,
                    end.isoformat() if end else None,
                    int(top_k),
                    use_trend_filter,
                )
            col_left, col_right = st.columns([2, 1])
            with col_left:
                render_nav(nav)
                if not selected.empty:
                    st.subheader("每期选择行业")
                    st.dataframe(selected, use_container_width=True)
            with col_right:
                render_stats(nav, returns)
