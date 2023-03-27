import socket

def handle_dns_request(data):
    # Parse the DNS request
    transaction_id = data[0:2]
    flags = data[2:4]
    qdcount = data[4:6]
    qname = data[12:-4].decode('utf-8')
    
    # Generate the DNS response dynamically
    response_ip = "192.168.1.1"
    response = transaction_id + flags + b'\x00\x01' + qdcount + b'\x00\x00\x00\x00'
    response += data[12:]
    response += b'\x00\x01\x00\x01\x00\x00\x02\x58\x00\x04' + socket.inet_aton(response_ip)
    
    return response

def main():
    # Create a UDP socket and bind it to port 53
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5053))
    
    while True:
        # Receive a DNS request
        data, addr = sock.recvfrom(1024)
        
        # Handle the DNS request and generate the response dynamically
        response = handle_dns_request(data)
        print("DND response:", response)
        
        # Send the DNS response back
        sock.sendto(response, addr)

if __name__ == '__main__':
    main()