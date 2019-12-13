# python-freeipa-json
Tiny/basic module for communicating with the FreeIPA API without having to install their entire toolchain
## Info
This module tries to use a minimal set of dependencies to communicate with FreeIPA through it's json rpc instead of using the official FreeIPA toolchain which is quite dependency heavy. Not all ipa functions has been added yet.
## Installation
Use the included setup.py to install or manually copy the ipahttp to your python library directory.
## Dependencies
- requests

## Example usage
```python
import ipahttp

ipa = ipahttp.ipa('ipa.example.com')
ipa.login('apiuser', 'secret_password')
reply = ipa.host_find()
for host in reply['result']['result']:
    print('Found host %s' % host['fqdn'][0])

first_name = "Fred"
second_name = "Idol"
user = ipa.user_find(attrs={"mail": "fred@example.com"})
if user["result"]["count"] < 1:
    result = ipa.user_add(user=first_name, opts={
        "givenname": first_name,
        "sn": second_name,
        "cn": "%s %s" % (first_name, second_name) 
    })
    if result["error"] is not None:
        print(result["error"])
    else:
        print("user %s %s was created", (first_name, second_name))
```

## License

MIT © [Nordnet Bank AB](https://www.nordnet.se/)
