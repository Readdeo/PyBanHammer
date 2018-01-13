# PyBannHammer
import requests, os, time

# You can change the link to the ip lists in blocklist.de
blocklist_link = 'https://lists.blocklist.de/lists/all.txt'

already_blocked = []
already_blocked_ip = 0
blocked_now = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    # Saving iptables rules to file
    print('Saving iptables rules to file')
    iptables_save = os.getcwd() + '/iptables-save.conf'
    os.system('iptables-save > ' + iptables_save)

    print('Reading file')
    with open(iptables_save, 'r') as f:
        rules = f.read()

    print("Creating list of already blocked ip's")
    for rule in rules.splitlines():
        if '-A INPUT -s ' in rule:
            if ' -j DROP' in rule:
                rule = rule.split()
                already_blocked.append(rule[3][:-3])

    for ip in already_blocked:
        already_blocked_ip = already_blocked_ip + 1
    print(str(already_blocked_ip)  + ' ip is blocked already')

    print('Getting blocklist')
    blocklist = requests.get(blocklist_link)

    blocklis_ips = 0
    for address in blocklist.text.splitlines():
        blocklis_ips = blocklis_ips +1
    print(str(blocklis_ips) + ' ip downloaded')

    time.sleep(5)

    print('Creating new rules')
    start_time = time.time()
    status_update_time = time.time()
    loops = 0
    for address in blocklist.text.splitlines():
        loops = loops + 1

        if address not in already_blocked:
            blocked_now = blocked_now + 1
            cmd = 'iptables -A INPUT -s {} -j DROP'.format(address)
            print('Blocking ip: ' + str(address))
            out = os.system(cmd)
            if str(out) != '0':
                print('iptables response: ' + str(out))
            if str(out) == '512':
                print('iptables could not block ipv6 address')
            if time.time() - status_update_time > 60:
                status_update_time = time.time()
                time_str = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
                est_time_sec = int(((time.time() - start_time) / loops) * blocklis_ips)
                est_time_str = time.strftime('%H:%M:%S', time.gmtime(est_time_sec))
                print(bcolors.OKGREEN + '')
                print('Elapsed time: ' + time_str)
                print('Progress: ' + str(loops) + '/' + str(blocklis_ips))
                print(str(blocked_now) + ' ip was blocked')
                print('Estimated time: ' + est_time_str)
                print('' + bcolors.ENDC)

    time_str = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))

    print('Process finished in ' + time_str)
    print(str(already_blocked_ip) + ' ip was blocked already')
    print(str(blocked_now) + ' ip was blocked now')

    # Logging to file
    current_time_str = time.strftime('%Y, %m %d %H:%M:%S',
                                              time.gmtime(time.time()))
    with open('log.txt', 'w+') as f:
        f.write('Last run: ' + current_time_str + '\n')
        f.write('Process finished in ' + time_str + '\n')
        f.write(str(already_blocked_ip) + ' ip was blocked already' + '\n')
        f.write(str(blocked_now) + ' ip was blocked now')
