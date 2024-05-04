from service.rule.rule_service import RuleService

if __name__ == '__main__':
    s = RuleService()
    s.start()
    s.register_mqtt_service()

    while True:
        if input("stop running [q]:") == 'q':
            break

    s.stop()
