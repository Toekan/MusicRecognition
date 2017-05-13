import multiprocessing as mp
import time
import recording as rc

def f(conn):
    recordinst = rc.Recording()
    record = 0
    send = 0
    t = int(5*44100/2048)
    print(t)
    for i in range(t):
        a = time.clock()
        y = recordinst.record()
        b = time.clock()
        conn.put(i)
        c = time.clock()
        record += (b - a)
        send += (c - b)
    time.sleep(0.1)
    print(record)
    print(send)
    print(conn.get())
    conn.close()

if __name__ == '__main__':
    q = mp.Queue()
    p = mp.Process(target=f, args=(q,))
    p.start()
    for i in range(107):
        q.get()
    q.put(True)
    time.sleep(1)
    p.terminate()
    time.sleep(0.1)
    print(p.is_alive())