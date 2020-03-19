import toml

#Simple parsing of toml config file, returns dictionaries of section or subsection

def config(filename, section, subsection = None):
    parser = toml.load(filename)
    if subsection is None:
        return parser[section]
    return parser[section][subsection]