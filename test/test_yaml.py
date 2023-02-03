from yaml_parser import yaml_hookers
from temp.entry import run


def main():
    with yaml_hookers('../example.yaml'):
        run()
    run()


if __name__ == '__main__':
    main()
