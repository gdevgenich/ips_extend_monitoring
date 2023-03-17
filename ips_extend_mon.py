from ips_extend_checker import IPSExtendChecker
from sys import argv


if __name__ == "__main__":
    name = argv[1] if len(argv) > 1 else "testing"
    ips_extend_checker = IPSExtendChecker(config_file="config.yaml", section_name=name)

    try:
        ips_extend_checker.read_data_from_config()
        ips_extend_checker.clients_init()
        ips_extend_checker.check()
    except Exception as e:
        pass
    ips_extend_checker.send_report()
