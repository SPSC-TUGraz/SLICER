def get_config(filename):
    # open file
    with open(filename, 'r', encoding='UTF-8') as file:
        # initialize dictionary
        config_values = {}

        # try whether file could be opened
        if file.closed:
            raise IOError('Target file cant be resolved.')

        # read lines until the end of the .txt file
        for line in file:
            # read line from the file
            line = line.strip()

            # Test for commented lines and empty lines
            if not line or line.startswith('%'):
                # ignore these lines
                continue

            # split line at the "=" sign
            parts = line.split('=')

            # Test for incomplete configuration arguments
            if len(parts) == 2 and parts[1].strip():
                # extract variable name and value
                var_name = parts[0].strip()
                var_value_str = parts[1].strip()

                # Test for number or string
                try:
                    var_value = float(var_value_str)
                except ValueError:
                    var_value = var_value_str

                # add name and value to dictionary
                config_values[var_name] = var_value
            else:
                # display warning for ignored lines
                print(f'Ignoring invalid line: {line}')

    return config_values

def main():
    filename = "own_tools/config.txt"
    config = get_config(filename)
    print(config)

if __name__ == "__main__":
    main()