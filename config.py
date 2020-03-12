from configparser import ConfigParser

def config(filename='database.ini', section='botconf'):

    parser = ConfigParser()
    parser.read(filename)
    conf = {}
    
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            conf[param[0]] = param[1]
            
    else:
        raise Exception(f'Section {section} not found in the {filename} file.')
    return conf

if __name__ == '__main__':
    print(config('database.ini', 'mysql'))