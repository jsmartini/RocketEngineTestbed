import toml

load = lambda : toml.load("./config.toml")

global CONFIG

CONFIG = load()

# loads toml configuration globally for all files that import * this

