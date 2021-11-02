import datetime


TS = lambda : datetime.datetime.now().timestamp() # timestamp macro


if __name__ == "__main__":
    print(TS())
