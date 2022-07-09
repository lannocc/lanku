from . import config

from lank.node import NODES, HELLO_TIMEOUT, GENERAL_TIMEOUT, KEEPALIVE
from lank.node.protocol.v2 import *
from lank.crypto import get_handler as get_crypto
from requests import get

from threading import Thread
from queue import Queue, Empty
import socket
import sys


class Client(Thread):
    def __init__(self, app, verbose=True):
        super().__init__(name='node-client')
        self.app = app
        self.verbose = verbose

        self.label = self.app.home.pnl_config.label.value
        self.pwd = self.app.home.pnl_config.pwd.value
        self.host = self.get_public_ip()
        self.port = int(self.app.home.pnl_config.peer_port.value)

        self.node = None
        self.ping = None
        self.input = Queue(maxsize=1)
        self.output = Queue()

        self.sender_thread = Thread(
            name='node-client-sender', target=self.sender)
        self.receiver_thread = Thread(
            name='node-client-receiver', target=self.receiver)

    def run(self):
        self.print(' - connecting to node:')

        for addr in NODES:
            self.print(f'   * trying {addr}... ', False)

            try:
                sock = socket.create_connection(addr, timeout=HELLO_TIMEOUT)
                sock.settimeout(HELLO_TIMEOUT)
                self.node = Handler(sock, addr)
                self.node.hello()
                self.node.sock.settimeout(GENERAL_TIMEOUT)
                self.print('[READY]')
                break

            except ConnectionRefusedError:
                self.print('[REFUSED]')
                self.node = None

            except socket.timeout:
                self.print('[TIMEOUT]')
                self.node = None

        if not self.node: return
        self.receiver_thread.start()
        self.sender_thread.start()

        self.input.put_nowait(GetRegistration(self.label))
        msg = self.output.get(timeout=GENERAL_TIMEOUT)
        if not msg: return
        if not isinstance(msg, Registration):
            return self.error(f'failed to get label info: {msg}')

        try:
            crypto = get_crypto(msg.version)
            priv_key = crypto.load_private_key(msg.key_pair_pem, self.pwd)

        except TypeError as e:
            return self.error(f'failed to unlock private key: {e}')
        except ValueError as e:
            return self.error(f'failed to unlock private key: {e}')

        msg = PeerOn(crypto.VERSION, self.label, self.host, self.port)
        msg.signature = crypto.sign(priv_key, msg.to_sign(crypto))

        self.input.put_nowait(msg)
        msg = self.output.get(timeout=GENERAL_TIMEOUT)
        if not msg: return
        if not isinstance(msg, Signed):
            return self.error(f'failed to sign on: {msg}')

        config.save_connect_label(self.label)

        self.input.put_nowait(ListLabels())
        msg = self.output.get(timeout=GENERAL_TIMEOUT)
        if not msg: return
        if not isinstance(msg, LabelsList):
            return self.error(f'failed to get labels list: {msg}')

        self.print(f'labels: {msg.labels}')
        del msg.labels[msg.labels.index(self.label)]
        self.app.home.pnl_labels.refresh_labels(msg.labels)

        for label in msg.labels:
            if label in self.app.home.pnl_labels.interests:
                self.input.put(LabelInterest(label))

    def notify(self, label, notify=True):
        self.input.put_nowait(
            LabelInterest(label) if notify else LabelIgnore(label))

    def stop(self):
        if not self.node: return
        node = self.node
        self.node = None

        node.sock.shutdown(socket.SHUT_RDWR)
        node.sock.close()
        self.output.put_nowait(None)
        self.input.put_nowait(None)

        self.app.home.pnl_labels.refresh_labels()

    def join(self):
        self.receiver_thread.join()
        super().join()

    def sender(self):
        try:
            while self.node:
                try:
                    #while msg := self.input.get(timeout=KEEPALIVE):
                    msg = self.input.get(timeout=KEEPALIVE)
                    if msg:
                        if not self.node: break
                        self.send(msg)

                except Empty:
                    if self.ping:
                        return self.error('ping sent but no pong received')

                    if self.node:
                        self.ping = Ping()
                        self.send(self.ping)

        finally:
            self.stop()

    def send(self, msg):
        if not self.node: return
        self.print(f'N    {self.node.addr} <- {msg}')
        self.node.send(msg)

    def receiver(self):
        try:
            #while msg := self.recv():
            msg = self.recv()
            while msg:
                if isinstance(msg, Pong):
                    if not self.ping:
                        return self.error(f'received pong without ping: {msg}')

                    if msg.nonce != self.ping.nonce:
                        return self.error(f'ping-pong nonce mismatch')

                    self.ping = None

                elif isinstance(msg, Signed) and msg.label != self.label:
                    self.app.notify(msg)

                else:
                    self.output.put(msg)

                msg = self.recv()

            self.error('lost connection')

        except OSError as e:
            self.error(e)

        finally:
            self.stop()

    def recv(self):
        if not self.node: return None
        msg = self.node.recv()
        if msg: self.print(f'N    {self.node.addr} -> {msg}')
        return msg

    def get_public_ip(self):
        ip = get('https://api.ipify.org').content.decode('utf-8')
        self.print(f' - our public IP address: {ip}')
        return ip

    def print(self, msg, newline=True):
        if not self.verbose: return

        if newline:
            print(msg)

        else:
            print(msg, end='')
            sys.stdout.flush()

    def error(self, e):
        if not self.node: return
        print(f'** ERROR ** {e}')
        self.stop()

