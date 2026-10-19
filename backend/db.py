"""SQLite demo data + read-only, parameterized queries. ALL DATA IS DEMO DATA."""
import random
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "demo.db"
GROUPS = {"failure_reason": "failure_reason", "payment_method": "payment_method"}  # whitelist


def seed():
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript("""
    CREATE TABLE orders(id INTEGER PRIMARY KEY, created_at TEXT, amount REAL, status TEXT, channel TEXT);
    CREATE TABLE payment_attempts(id INTEGER PRIMARY KEY, order_id INTEGER, created_at TEXT,
        status TEXT, failure_reason TEXT, payment_method TEXT);
    """)
    rng = random.Random(42)
    # (date, failure probability): day 2 has far more failures. Both days cover 00:00-14:59.
    for day, p_fail in (("2025-01-14", 0.07), ("2025-01-15", 0.32)):
        for hour in range(0, 15):
            for _ in range(rng.randint(10, 14) if hour >= 8 else rng.randint(2, 4)):
                ts = f"{day} {hour:02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"
                method = rng.choice(["card", "card", "card", "wallet", "bank_transfer"])
                failed = rng.random() < (p_fail * (1.6 if method == "card" else 0.4) if day.endswith("15") else p_fail)
                reason = None
                if failed:
                    reason = rng.choice(["issuer_timeout"] * 5 + ["insufficient_funds", "card_declined"]) \
                        if day.endswith("15") else rng.choice(["insufficient_funds", "card_declined", "issuer_timeout"])
                cur = con.execute("INSERT INTO orders(created_at,amount,status,channel) VALUES(?,?,?,?)",
                                  (ts, round(rng.uniform(20, 120), 2), "unpaid" if failed else "paid",
                                   rng.choice(["web", "app"])))
                con.execute("INSERT INTO payment_attempts(order_id,created_at,status,failure_reason,payment_method) "
                            "VALUES(?,?,?,?,?)", (cur.lastrowid, ts, "failed" if failed else "success", reason, method))
    con.commit()
    con.close()


def _ro():
    return sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)


def window():
    """Today = latest date in data; yesterday = the day before. Same time-of-day window on both."""
    with _ro() as c:
        today, end = c.execute("SELECT date(max(created_at)), time(max(created_at)) FROM orders").fetchone()
        yesterday = c.execute("SELECT date(?, '-1 day')", (today,)).fetchone()[0]
    return today, yesterday, end


def _day_metrics(c, day, end):
    rev, paid = c.execute("SELECT COALESCE(SUM(amount),0), COUNT(*) FROM orders "
                          "WHERE status='paid' AND date(created_at)=? AND time(created_at)<=?", (day, end)).fetchone()
    att, failed = c.execute("SELECT COUNT(*), COALESCE(SUM(status='failed'),0) FROM payment_attempts "
                            "WHERE date(created_at)=? AND time(created_at)<=?", (day, end)).fetchone()
    return {"date": day, "revenue": round(rev, 2), "successful_orders": paid, "payment_attempts": att,
            "failed_attempts": failed, "failure_rate_pct": round(100 * failed / att, 1) if att else 0.0}


def compare_metrics():
    """Revenue, successful orders, failure rate: today vs yesterday, matching windows."""
    today, yesterday, end = window()
    with _ro() as c:
        return {"demo_data": True, "window": f"00:00:00-{end} on both days",
                "today": _day_metrics(c, today, end), "yesterday": _day_metrics(c, yesterday, end)}


def failure_breakdown(group_by: str):
    """Failed attempts per group (failure_reason or payment_method), today vs yesterday, matching windows."""
    col = GROUPS.get(group_by)
    if not col:
        return {"error": f"group_by must be one of {list(GROUPS)}"}
    today, yesterday, end = window()
    out = {"demo_data": True, "group_by": group_by, "window": f"00:00:00-{end} on both days"}
    with _ro() as c:
        for label, day in (("today", today), ("yesterday", yesterday)):
            rows = c.execute(f"SELECT COALESCE({col},'none'), COUNT(*) FROM payment_attempts "  # col is whitelisted
                             "WHERE status='failed' AND date(created_at)=? AND time(created_at)<=? "
                             "GROUP BY 1 ORDER BY 2 DESC", (day, end)).fetchall()
            out[label] = {k: n for k, n in rows}
    return out
