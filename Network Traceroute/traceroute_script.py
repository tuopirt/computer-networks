import subprocess

def traceroute(site):
    try:
        result = subprocess.run(["traceroute", site], capture_output=True, timeout=20)

        if result.returncode != 0:
            print("Traceroute: failed")
            return

        #print(result.stdout)

        line_count = len(result.stdout.splitlines()) - 1
        print(line_count, "hops to", host_name)
    except subprocess.TimeoutExpired:
        print("Traceroute: failed (exceed time limit)")
        return

host_name = input("Enter a server name:\n")
traceroute(host_name)