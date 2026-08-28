from apscheduler.schedulers.blocking import BlockingScheduler
import config
from jobs.apex_signal import run as run_signal
from jobs.monitor import run as run_monitor
from jobs.health import run as run_health
from jobs.weekly import run as run_weekly
from jobs.collect import run as run_collect


sched = BlockingScheduler(timezone="UTC")

# كل 5 دقائق — إدارة الصفقات
sched.add_job(run_monitor, "interval", minutes=5, id="monitor")

# يومياً — إشارة
sched.add_job(run_signal, "cron", hour=config.SIGNAL_HOUR_UTC, minute=5, id="signal")

# كل 4 ساعات — جمع البيانات
sched.add_job(run_collect, "cron", hour="0,4,8,12,16,20", minute=0, id="collect")

# كل ساعة — فحص صحة
sched.add_job(run_health, "cron", minute=17, id="health")

# أسبوعياً — تقرير
sched.add_job(run_weekly, "cron", day_of_week="sun", hour=18, minute=0, id="weekly")


if __name__ == "__main__":
    print("⏰ APEX V3 Scheduler running...")
    print(f"📡 Signal daily at {config.SIGNAL_HOUR_UTC}:05 UTC")
    print("🔍 Monitor every 5 minutes")
    print("📊 Collect every 4 hours")
    print("🏥 Health check hourly")
    print("📋 Weekly report Sunday 18:00 UTC")

    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass
