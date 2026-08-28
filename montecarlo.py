import numpy as np
from sizing import monte_carlo_sim


def run():
    print("=" * 50)
    print("محاكاة مونت كارلو — سلم المخاطرة")
    print("=" * 50)

    # مثال: نتائج تاريخية بـ R (عدّل حسب نتائجك)
    sample_returns = [3.2, -1, -1, 3.2, -1, 2.0, -1, 3.2, -1, -1,
                      3.2, 3.2, -1, -1, 3.2, -1, 2.0, 3.2, -1, -1]

    print(f"\nعينة الصفقات: {len(sample_returns)}")
    print(f"نسبة النجاح: {sum(1 for r in sample_returns if r > 0) / len(sample_returns) * 100:.1f}%")
    print(f"متوسط R: {np.mean(sample_returns):.2f}")

    results = monte_carlo_sim(sample_returns)

    print(f"\nنتائج 4000 مسار:")
    print(f"  - المتوسط: {results['median']:.1f}R")
    print(f"  - أسوأ 5%: {results['worst_5']:.1f}R")
    print(f"  - أقصى انخفاض: {results['max_dd']:.1f}R")

    print("\n" + "=" * 50)

    if results["worst_5"] < -4:
        print("⚠️ المخاطرة الحالية مرتفعة — قلل الحجم")
    else:
        print("✅ المخاطرة مقبولة")


if __name__ == "__main__":
    run()
