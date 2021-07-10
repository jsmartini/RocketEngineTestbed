import toml

load = lambda : toml.load("./config.toml")

def init():
    """
    
    Initializes all hardware
    
    """

    return



if __name__ == "__main__":
    print(load())