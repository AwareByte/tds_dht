import time
import board
import adafruit_dht
from pyiArduinoI2Ctds import *
import sys
import threading
#from queue import Queue
from collections import deque

array_size = 10
temperature_queue = deque(maxlen=array_size)
humidity_queue = deque(maxlen=array_size)
tds_queue = deque(maxlen=array_size)
ec_queue = deque(maxlen=array_size)

queue_lock = threading.Lock()


def _tds_start():
    tds = pyiArduinoI2Ctds(0x09, NO_BEGIN)
    if tds.begin():
        print("Найден датчик tds")
        return tds
    else:
        print("Датчик не найден!")
        return None

#start connections
# DHT
dhtDevice = adafruit_dht.DHT11(board.D4)
print("Найден датчик dht")

# TDS
tds = _tds_start()

def measure_dht():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if not temperature:
            temperature = 20
        if not humidity:
            humidity = 37
    except:
        temperature = 20
        humidity = -1
    return humidity,temperature

def measure_tds(temp):
    try:
        tds.set_t(temp)
        tds_value = tds.getTDS()
        ec_value = tds.getEC()
    except:
        # Ошибка
        tds_value = -1
        ec_value = -1
    return tds_value,ec_value

def fill_arrays():
    while True:
        humidity,temperature = measure_dht();
        tds_value,ec_value = measure_tds(temperature);
        with queue_lock:
            humidity_queue.append(humidity)
            temperature_queue.append(temperature)
            tds_queue.append(tds_value)
            ec_queue.append(ec_value)
        print("temp ",list(temperature_queue))
        print("humidity ",list(humidity_queue))
        print("tds ",list(tds_queue))
        print("ec ",list(ec_queue))
        time.sleep(1)

writer_thread = threading.Thread(target=fill_arrays)
writer_thread.start()

def get_values():
    humidity = -1;
    temperature = -1;
    tds_value = -1;
    ec_value = -1;
    with queue_lock:
        temperature_arr = list(temperature_queue)
        humidity_arr = list(humidity_queue)
        tds_arr = list(tds_queue)
        ec_arr = list(ec_queue)
        humidity_arr = [x for x in humidity_arr if x != -1]
        temperature_arr = [x for x in temperature_arr if x != -1]
        tds_arr = [x for x in tds_arr if x != -1]
        ec_arr = [x for x in ec_arr if x != -1]
        try:
            humidity = sum(humidity_arr) / len(humidity_arr)
        except:
            pass
        try:
            temperature = sum(temperature_arr) / len(temperature_arr)
        except:
            pass
        try:
            tds_value = sum(tds_arr) / len(tds_arr)
        except:
            pass
        try:
            ec_value = sum(ec_arr) / len(ec_arr)
        except:
            pass
    return temperature,humidity,tds_value,ec_value
