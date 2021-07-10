import toml

load = lambda : toml.load("./config.toml")

def init():
    """
    
    Initializes all hardware
    
    """

    return

global CONFIG
CONFIG = load()
init()

if __name__ == "__main__":
    print(load())