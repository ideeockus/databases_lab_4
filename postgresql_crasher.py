import random
import time
from concurrent.futures import ProcessPoolExecutor
import subprocess
import json

import psycopg
from psycopg_pool import ConnectionPool
from tqdm import tqdm


db_url = 'postgres://postgres:pass123@localhost:5433/test_db_1'

pool = ConnectionPool(db_url, max_size=100, open=True)


def insert_random_num():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            rand_num = random.randint(-2_147_483_648, 2_147_383_647)
            for i in tqdm(range(100_000)):
                # number = random.randint(-2_147_483_648, 2_147_483_647)
                number = rand_num + i
                cur.execute(
                        "INSERT INTO table_1 (x, y) VALUES (%s, %s)",
                        (rand_num, number))
            try:
                conn.commit()
                print("COMMITED")
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                print("ROLLBACKED")


def set_cluster_alive_info(instance: int, alive: bool, info={}):
    if info.get(instance) == alive:
        return
    else:
        info[instance] = alive
        print(f'instance {instance} is {alive}')



def run_cluster_monitoring() -> dict[str, int | float]:
    print('Run monitoring')

    db_instances_ports = [
        '5433',
        '5434',
        '5435',
    ]

    stats = []
    interval_sec = 1 / 10  # 100 ms

    start = time.time()
    while True:
        is_clsuter_alive = False
        for instance_port in db_instances_ports:
            instance_state = subprocess.call([
                'pg_isready',
                '-q',
                '-h', 'localhost',
                '-p', instance_port,
            ])
            stats.append({
                'ts': time.time(),
                'instance_port': instance_port,
                'state': instance_state,
            })

            set_cluster_alive_info(instance_port, instance_state==0)
            is_clsuter_alive |= instance_state==0

        # if not is_clsuter_alive or (time.time() - start >= 20):
        if not is_clsuter_alive:
            break

        # wait next
        delta = time.time() - start
        time.sleep(interval_sec - (delta % interval_sec))

    return stats


def save_data(data: dict):
    with open('monitoring_data.json', 'w') as f:
        f.write(json.dumps(data))


if __name__ == '__main__':
    print('Start crasher.py')

    executor = ProcessPoolExecutor(max_workers=16)
    monitoring_future = executor.submit(run_cluster_monitoring)
    # run monitoring

    time.sleep(1)

    for i in range(1, 100):
        future = executor.submit(insert_random_num)

    # insert_random_num()

    print('Done crasher.py')
    executor.shutdown(wait=False, cancel_futures=True)

    stats = monitoring_future.result()
    save_data(stats)
    print('Data saved')


