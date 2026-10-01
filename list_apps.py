# Makes it easier to find the app ids
import json
import subprocess


def get_webos_version():
    """Return the webOS major version (mirrors magic_mapper.py)."""
    try:
        with open("/etc/starfish-release") as f:
            release = f.read()
        return int(release.split()[2].split(".")[0])
    except (OSError, IndexError, ValueError):
        return 0


endpoint = "luna://com.palm.applicationManager/listLaunchPoints"
payload = {}

# webOS 10.x (Rockhopper) regression: `luna-send -n 1` is a silent no-op -- it
# neither prints a response nor delivers the message, so this helper prints
# nothing (and json.loads() then fails on empty output). `-t 1` delivers exactly
# once, but the JSON payload comes back on STDERR behind a "timingServiceResponse"
# line, so recover it from there. Gated on version so pre-10 devices keep the
# original `-n 1` path. Mirrors the same fix in magic_mapper.py's luna_send().
if get_webos_version() >= 10:
    command = ["/usr/bin/luna-send", "-t", "1", endpoint, json.dumps(payload)]
    print("running command: %s" % command)
    proc = subprocess.run(command, capture_output=True)
    output = proc.stdout.decode("utf-8", "replace")
    for line in proc.stderr.decode("utf-8", "replace").splitlines():
        if "timingServiceResponse" in line and "{" in line:
            output = line[line.find("{"):]
            break
else:
    command = ["/usr/bin/luna-send", "-n", "1"]
    command.append(endpoint)
    command.append(json.dumps(payload))
    print("running command: %s" % command)
    output = subprocess.check_output(command)

output_dict = json.loads(output)

apps = output_dict['launchPoints']
print(apps)
for app in apps:
    print(app['title'] + " : " + app['id'])
