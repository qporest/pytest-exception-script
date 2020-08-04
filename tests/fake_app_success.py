import time

import logging
LOG = logging.getLogger(__name__)
# LOG.addHandler(logging.FileHandler(
#     "/Users/ihor.husar@ibm.com/temp/chaos-test/tests/fake_app.log"))
LOG.setLevel(logging.INFO)

def unused_method():
    pass

def get_data():
    pass

def process_data():
    pass

def main():
    while True:
        try:
            LOG.info("Running")
            get_data()
            
            time.sleep(1)
        except KeyError as e:
            LOG.info("I can process this error without quitting")
        except Exception as e:
            LOG.info("An exception happened")
            LOG.info(e)
            break
        process_data()

def factory():
    return main

if __name__=="__main__":
    import threading
    th = threading.Thread(target=main)
    th.daemon = True
    th.start()

    while True:
        print(th.isAlive())
