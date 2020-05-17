# FixMyPPPoE

FixMyPPPoE is a Python utility that can log into your home router over the web interface and force your router to re-dial the configured PPPoE or switch between WAN settings on your home router. (Say you want to alternate between two ISPs running off of the same physical link)

# Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install 
```bash
pip install https://github.com/sarfarazahmad89/FixMyPPPoE
```

## Usage
```bash
Usage: fixmypppoe [OPTIONS]

  The script flips through different WAN options (PPPoE, Ethernet) on your
  router. This could serve following purposes:

  *  Your PPPoE connection just dies periodically and you want your router
  to     dial it again but what you have is a cheap, $10 router that doesn't
  automatically re-dial and doesn't provide any ssh/telnet interface to
  make automate re-dialing easier either. So you use selenium to interact
  with the router over the web interface.

  *  If you are in a situation like mine, where you can alternatively switch
  between operators over the same physical link. You can use this script
  to flip between operators.

  Tips: * You can use a combination of --no-headless, --run-every and
  --on-ping-fail options to automatically detect connection failures   and
  re-dial. Cloudflare's DNS service at 1.1.1.1 is pinged to check    network
  availability. * The script calls up ipinfo.io and logs the details

  Requirements:  selenium, chrome(browser), pyvirtualdisplay, click,
  requests

Options:
  -s, --sequence TEXT  The order in which to sequentially change the WAN
                       connection type. E.g. "PPPoE:Static IP:PPPoE"
                       [required]

  --no-headless        Don't be headless ! Show me the Chrome window.
  --on-ping-fail       Run the flip sequence only when ping fails
  --run-every INTEGER  Run the flip sequence every these many seconds.
  --no-ipinfo TEXT     Don't query ipinfo.io.
  --debug              Don't log debug messages.
  --help               Show this message and exit.
```
