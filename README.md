# CS5700_CDN


# Testing
### End to End
- Create a Ubuntu VM to test in isolation.
- Add `nameserver 198.74.61.103` to `/etc/resolv.conf`. Don't remove default nameserver as it will act as fallback. Note: `198.74.61.103` is ip address of dns server `cdn-dns.5700.network`
- Redirect traffic on port `53` of `198.74.61.103` to port `20200`. This is needed as `resolv.conf` by default sends DNS request to port `53` and does not support custom port.
```
sudo iptables -t nat -A OUTPUT -p udp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
sudo iptables -t nat -A OUTPUT -p tcp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
```
- Run following command to download file
```
wget http://cs5700cdn.example.com:20200/2026_FIFA_World_Cup
```
