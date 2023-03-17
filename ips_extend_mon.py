from ips_extend_checker import IPSExtendChecker

ips_extend_checker = IPSExtendChecker(config_file="config.yaml", section_name="testing")
errors = None

try:
    ips_extend_checker.read_data_from_config()
    ips_extend_checker.clients_init()
    ips_extend_checker.check()
except Exception as e:
    errors = str(e)
