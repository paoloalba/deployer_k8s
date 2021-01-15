import base64

def encodeb64(message, print_output=False):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    if print_output:
        print(base64_message)

    return base64_message

if __name__ == "__main__":
    msg_list = []
    msg_list.append("ciao")

    for mmm in msg_list:
        encodeb64(mmm, print_output=True)