from ips_extend_checker import IPSExtendChecker
from sys import argv
import asyncio

if __name__ == "__main__":
    name = argv[1] if len(argv) > 1 else "testing"
    ips_extend_checker = IPSExtendChecker(config_file="config.yaml", section_name=name)

    try:
        ips_extend_checker.read_data_from_config()
        ips_extend_checker.set_logging()
        ips_extend_checker.clients_init()
        ips_extend_checker.check()
    except Exception as e:
        ips_extend_checker.error_message = str(e)
    if ips_extend_checker.error_message is not None:
        try:
            ips_extend_checker.error_message = None
            ips_extend_checker.clients_stop()
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
            ips_extend_checker.clients_init()
            ips_extend_checker.check()
        except Exception as e:
            ips_extend_checker.error_message = str(e)
    try:
        ips_extend_checker.clients_stop()
    except:
        pass
    ips_extend_checker.send_report()
