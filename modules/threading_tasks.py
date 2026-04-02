import threading

def run_in_thread(func, *args):
    thread = threading.Thread(target=func, args=args)
    thread.start()
    return thread