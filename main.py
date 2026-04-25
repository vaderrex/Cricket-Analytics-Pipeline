import argparse
import time
import schedule
import logging
import sys

from etl.orchestrator import Pipeline
from config.config import cfg

# setup logs
logging.basicConfig(
    level=cfg.L_LEVEL,
    format='%(asctime)s | %(levelname)s | %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("MAIN")

def run_job():
    try:
        p = Pipeline()
        p.run()
    except Exception as e:
        logger.error(f"FAIL: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--now", action="store_true")
    
    args = p.parse_args()

    if args.now:
        logger.info("running once now...")
        run_job()
    else:
        logger.info(f"scheduler on ({cfg.INTERVAL}h)")
        run_job() # run first
        
        schedule.every(cfg.INTERVAL).hours.do(run_job)
        while 1:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
