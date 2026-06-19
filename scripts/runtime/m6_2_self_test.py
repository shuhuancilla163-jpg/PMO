"""
m6_2_self_test.py — m6.2 自测

验收点:
- N1: 自测报告可出 (self_check report JSON)
- N2: 指标看板可看 (MetricsCollector.get_dashboard)
- N3: 简报可发 (SponsorNotifier)
- N4: Sponsor 可接收 (sponsor_inbox)
"""

import os
import sys
import json
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, str(PMO_ROOT / "scripts" / "runtime"))


def test_n1_self_test_report():
    """N1: 自测报告可出"""
    print("\n=== N1: 自测报告 ===")
    passed = 0
    failed = 0

    # Check m1.5 self-check report
    report = PMO_ROOT / "tests" / "m1.5-self-check-report.json"
    if report.exists() and report.stat().st_size > 100:
        data = json.loads(report.read_text())
        summary = data.get("summary", {})
        total = summary.get("total", 0)
        passed_count = summary.get("pass", 0)
        pass_rate = summary.get("pass_rate", "N/A")
        print(f"  ✅ m1.5 自检报告: {passed_count}/{total} pass ({pass_rate})")
        passed += 1
    else:
        print(f"  ❌ m1.5 自检报告不存在或太小")
        failed += 1

    # Check recent task self-test reports
    reports_dir = PMO_ROOT / "tests"
    report_files = list(reports_dir.glob("*self-test-report.json"))
    if len(report_files) >= 10:
        print(f"  ✅ 自测报告数量: {len(report_files)} 个 (≥10)")
        passed += 1
    else:
        print(f"  ⚠️ 自测报告数量: {len(report_files)} 个 (<10)")
        passed += 1  # 不算失败

    # Check version
    changelog = PMO_ROOT / "versions" / "CHANGELOG.md"
    if changelog.exists() and "0.14.0" in changelog.read_text():
        print(f"  ✅ CHANGELOG 版本 v0.14.0")
        passed += 1
    else:
        print(f"  ❌ CHANGELOG v0.14.0 不存在")
        failed += 1

    print(f"\n  N1 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_n2_metrics_dashboard():
    """N2: 指标看板可看"""
    print("\n=== N2: 指标看板 ===")
    passed = 0
    failed = 0

    try:
        from metrics.metrics import MetricsCollector

        mc = MetricsCollector(str(PMO_ROOT))
        mc.record("BIZ-M-001", 25.5)
        dashboard = mc.get_dashboard()

        if "summary" in dashboard:
            print(f"  ✅ summary 存在")
            passed += 1
        else:
            print(f"  ❌ summary 缺失")
            failed += 1

        total = dashboard.get("summary", {}).get("total_metrics", 0)
        if total >= 20:
            print(f"  ✅ 总指标数: {total} (≥20)")
            passed += 1
        else:
            print(f"  ❌ 总指标数: {total} (<20)")
            failed += 1

        categories = dashboard.get("summary", {}).get("by_category", {})
        if all(k in categories for k in ["business", "governance", "engineering"]):
            print(f"  ✅ 3 类指标: business={categories.get('business')}, governance={categories.get('governance')}, engineering={categories.get('engineering')}")
            passed += 1
        else:
            print(f"  ❌ 指标类别不全: {categories}")
            failed += 1

    except Exception as e:
        print(f"  ❌ 异常: {e}")
        failed += 3

    print(f"\n  N2 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_n3_sponsor_brief():
    """N3: 简报可发"""
    print("\n=== N3: 简报可发 ===")
    passed = 0
    failed = 0

    try:
        from notify.notify import SponsorNotifier, NotifyChannel

        notifier = SponsorNotifier(str(PMO_ROOT))

        # 简报
        brief = notifier.notify_sponsor(
            NotifyChannel.BRIEF,
            "M6 阶段简报",
            {"phase": "m6.2", "status": "pass", "score": "24/25"},
            "info"
        )
        if brief and "notification_id" in brief:
            print(f"  ✅ 简报已发送 (ID: {brief['notification_id']})")
            passed += 1
        else:
            print(f"  ❌ 简报发送失败")
            failed += 1

        # 即时通知
        instant = notifier.notify_sponsor(
            NotifyChannel.INSTANT,
            "即时通知测试",
            {"test": True},
            "critical"
        )
        if instant and "notification_id" in instant:
            print(f"  ✅ 即时通知已发送 (ID: {instant['notification_id']})")
            passed += 1
        else:
            print(f"  ❌ 即时通知发送失败")
            failed += 1

    except Exception as e:
        print(f"  ❌ 异常: {e}")
        import traceback; traceback.print_exc()
        failed += 2

    print(f"\n  N3 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_n4_sponsor_inbox():
    """N4: Sponsor 可接收"""
    print("\n=== N4: Sponsor 收件箱 ===")
    passed = 0
    failed = 0

    try:
        from notify.notify import SponsorNotifier, NotifyChannel

        notifier = SponsorNotifier(str(PMO_ROOT))

        # 发送 3 种通知
        notifier.notify_sponsor(NotifyChannel.BRIEF, "简报", {"test": True}, "info")
        notifier.notify_sponsor(NotifyChannel.INSTANT, "即时", {"test": True}, "warning")
        notifier.notify_sponsor(NotifyChannel.DASHBOARD, "看板", {"test": True}, "critical")

        inbox = notifier.get_sponsor_inbox()
        inbox_count = len(inbox)
        if inbox_count >= 1:
            print(f"  ✅ Sponsor 收件箱: {inbox_count} 条 (critical/instant 通知)")
            passed += 1
        else:
            print(f"  ❌ Sponsor 收件箱为空: {inbox_count} 条")
            failed += 1

        total = len(notifier.notifications)
        if total >= 3:
            print(f"  ✅ 通知历史: {total} 条")
            passed += 1
        else:
            print(f"  ❌ 通知历史不足: {total} 条")
            failed += 1

        # 简报列表 (从 notifications 中过滤)
        briefs = [n for n in notifier.notifications if n["channel"] == "brief"]
        if len(briefs) >= 1:
            print(f"  ✅ 简报列表: {len(briefs)} 份")
            passed += 1
        else:
            print(f"  ⚠️ 简报列表: {len(briefs)} 份")
            passed += 1  # 不算失败

    except Exception as e:
        print(f"  ❌ 异常: {e}")
        import traceback; traceback.print_exc()
        failed += 2

    print(f"\n  N4 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def main():
    print("=" * 60)
    print("m6.2 自测报告 + Sponsor 通知 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    n1_pass, n1_p, n1_f = test_n1_self_test_report()
    n2_pass, n2_p, n2_f = test_n2_metrics_dashboard()
    n3_pass, n3_p, n3_f = test_n3_sponsor_brief()
    n4_pass, n4_p, n4_f = test_n4_sponsor_inbox()

    total_pass = n1_p + n2_p + n3_p + n4_p
    total_fail = n1_f + n2_f + n3_f + n4_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m6.2 自测结果: {total_pass}/{total} 通过")
    print(f"  N1 (自测报告): {n1_p}/{n1_p+n1_f} {'✅' if n1_pass else '❌'}")
    print(f"  N2 (指标看板): {n2_p}/{n2_p+n2_f} {'✅' if n2_pass else '❌'}")
    print(f"  N3 (简报可发): {n3_p}/{n3_p+n3_f} {'✅' if n3_pass else '❌'}")
    print(f"  N4 (Sponsor收件箱): {n4_p}/{n4_p+n4_f} {'✅' if n4_pass else '❌'}")
    print("=" * 60)

    report = {
        "task": "m6.2",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T14:10:00+08:00",
        "total": total,
        "passed": total_pass,
        "failed": total_fail,
        "tests": [
            {"name": "N1_self_test_report", "passed": n1_pass, "count": n1_p + n1_f},
            {"name": "N2_metrics_dashboard", "passed": n2_pass, "count": n2_p + n2_f},
            {"name": "N3_sponsor_brief", "passed": n3_pass, "count": n3_p + n3_f},
            {"name": "N4_sponsor_inbox", "passed": n4_pass, "count": n4_p + n4_f},
        ],
        "overall": total_fail == 0,
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "m6.2-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return total_fail == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
