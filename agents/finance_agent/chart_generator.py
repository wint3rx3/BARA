import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

# 디렉토리 설정
DATA_DIR = Path("data")
CHART_DIR = Path("charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)


def chart_stock_generator():
    data_path = DATA_DIR / "stock_data.csv"
    output_path = CHART_DIR / "stock_chart1.png"

    df = pd.read_csv(data_path)
    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Close"])
    df = df.sort_values("Date")

    plt.figure(figsize=(10, 6), facecolor="white")
    plt.plot(df["Date"], df["Close"], color="blue", linewidth=2)
    plt.grid(True, linestyle="--", color="lightgray")
    plt.title("Stock Price Trend", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Close Price", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print("✅ stock_chart1.png 생성 완료")


def chart_revenue_generator():
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    df = pd.read_csv(DATA_DIR / "revenue_data.csv")
    priority_cols = ["매출액", "영업이익", "당기순이익", "자산총계"]
    valid_col = next((col for col in priority_cols if col in df.columns and df[col].notna().all()), None)

    if valid_col is None:
        raise ValueError("모든 지표 컬럼에 결측치가 존재하거나 없음")

    df["연도"] = pd.to_numeric(df["연도"], errors="coerce")
    df = df.dropna(subset=["연도", valid_col]).sort_values("연도")

    # ✅ 쉼표 제거 + float 변환 + 조 단위 환산
    df[valid_col] = df[valid_col].str.replace(",", "").astype(float) / 1e12

    plt.figure(figsize=(10, 6), facecolor="white")
    plt.plot(df["연도"], df[valid_col], marker="o", color="green", linewidth=2)
    plt.grid(True, linestyle="--", color="lightgray")
    plt.title("Annual Revenue (in Trillion)", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Revenue (₩ Trillion)", fontsize=12)
    plt.xticks(df["연도"])
    plt.tight_layout()
    plt.savefig(CHART_DIR / "revenue_chart1.png")
    plt.close()
    print(f"✅ revenue_chart.png1 생성 완료 → 기준 컬럼: {valid_col}")


def concat_images(stock_path, revenue_path, combined_path):
    img1 = Image.open(stock_path)
    img2 = Image.open(revenue_path)

    width = img1.width + img2.width
    height = max(img1.height, img2.height)

    dst = Image.new("RGB", (width, height), "white")  # ✅ 크기 튜플 올바르게 수정
    dst.paste(img1, (0, 0))
    dst.paste(img2, (img1.width, 0))

    dst.save(combined_path)
    print("✅ 차트 병합 완료:", combined_path)



def to_windows_uri(path: Path) -> str:
    return path.resolve().as_uri()


def run(state: dict) -> dict:
    chart_stock_generator()
    chart_revenue_generator()

    stock_path = CHART_DIR / "stock_chart1.png"
    revenue_path = CHART_DIR / "revenue_chart1.png"
    combined_path = CHART_DIR / "finance_combined_chart1.png"

    concat_images(stock_path, revenue_path, combined_path)

    state["finance_result"] = {
        "agent": "AgentFinance",
        "output": {
            "combined_chart_path": to_windows_uri(combined_path),  # ✅ 이것만 남김
            "insight": "차트 기반 재무 인사이트는 추후 생성됩니다."
        },
        "error": None,
        "retry": False
    }
    return state

