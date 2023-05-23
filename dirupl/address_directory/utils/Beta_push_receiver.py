# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# For more information, please refer to <http://unlicense.org/>

# Reworked version of Push_receiver by MatthieuLemoine and Franc[e]sco #

from struct import unpack
import select
from .mcs_pb2 import *
import logging
from base64 import urlsafe_b64decode
import json
import time
from threading import Thread
import socket
import ssl
from asyncio import create_task, sleep

try:
  FileExistsError
except NameError:
  FileExistsError = OSError
  FileNotFoundError = IOError

log = logging.getLogger("push_receiver")


class PushReceiver:
  READ_TIMEOUT_SECS = 60 * 60
  MIN_RESET_INTERVAL_SECS = 5 * 60
  MAX_SILENT_INTERVAL_SECS = 60 * 60
  MCS_VERSION = 41

  PACKET_BY_TAG = [
      HeartbeatPing,
      HeartbeatAck,
      LoginRequest,
      LoginResponse,
      Close,
      "MessageStanza",
      "PresenceStanza",
      IqStanza,
      DataMessageStanza,
      "BatchPresenceStanza",
      StreamErrorStanza,
      "HttpRequest",
      "HttpResponse",
      "BindAccountRequest",
      "BindAccountResponse",
      "TalkMetadata"
  ]

  last_reset = 0


  def __init__(self, credentials, received_persistent_ids=[]):
    """
    initializes the receiver

    credentials: credentials object returned by register()
    received_persistent_ids: any persistent id's you already received.
                             array of strings
    """

    self.credentials = credentials
    self.persistent_ids = received_persistent_ids
    self.time_last_message_received = time.time()


  def __del__(self):
    # try:
    #   self.checkin_thread.cancel()
    # except AttributeError:
    #   pass
    try:
      self.socket.shutdown(socket.SHUT_RDWR)
      self.socket.close()
    except OSError as e:
      log.debug(f"Unable to close connection {e}")


  async def read(self, size):
    buf = b''
    while len(buf) < size:
      buf += await self.socket.recv(size - len(buf))
    return buf


  # protobuf variable length integers are encoded in base 128
  # each byte contains 7 bits of the integer and the msb is set if there's
  # more. pretty simple to implement


  async def read_varint32(self):
    res = 0
    shift = 0
    while True:
      b, = unpack("B", await self.read(1))
      res |= (b & 0x7F) << shift
      if (b & 0x80) == 0:
        break
      shift += 7
    return res


  def encode_varint32(self, x):
    res = bytearray([])
    while x != 0:
      b = (x & 0x7F)
      x >>= 7
      if x != 0:
        b |= 0x80
      res.append(b)
    return bytes(res)


  async def send(self, packet):
    header = bytearray([self.MCS_VERSION, self.PACKET_BY_TAG.index(type(packet))])
    log.debug(f'Packet to send:\n{packet}')
    payload = packet.SerializeToString()
    buf = bytes(header) + self.encode_varint32(len(payload)) + payload
    n = len(buf)
    total = 0
    while total < n:
      sent = self.socket.send(buf[total:])
      if sent == 0:
        raise RuntimeError("socket connection broken")
      total += sent


  async def recv(self, first=False):
    try:
      readable, _, _ = select.select([self.socket,], [], [], self.READ_TIMEOUT_SECS)
      if len(readable) == 0:
        log.debug("Select read timeout")
        return None
    except select.error as e:
      log.debug(f"Select error: {e}")
      return None
    try:
      if first:
        version, tag = unpack("BB", self.read(2))
        log.debug("version {}".format(version))
        if version < self.MCS_VERSION and version != 38:
          raise RuntimeError("protocol version {} unsupported".format(version))
      else:
        tag, = unpack("B", self.read(1))
      size = self.read_varint32()
    except OSError as e:
      log.debug(f"Read error: {e}")
      return None
    log.debug("Received message with tag {} ({}), size {}".format(tag, self.PACKET_BY_TAG[tag], size))
    self.time_last_message_received = time.time()
    if size >= 0:
      buf = self.read(size)
      Packet = self.PACKET_BY_TAG[tag]
      payload = Packet()
      payload.ParseFromString(buf)
      log.debug(f'Receive payload:\n{payload}')
      return payload
    return None


  def app_data_by_key(self, p, key, blow_shit_up=True):
    for x in p.app_data:
      if x.key == key:
        return x.value
    if blow_shit_up:
      raise RuntimeError("couldn't find in app_data {}".format(key))
    return None


  async def open(self):
    HOST = "mtalk.google.com"
    context = ssl.create_default_context()
    sock = socket.create_connection((HOST, 5228))
    self.socket = context.wrap_socket(sock, server_hostname=HOST)
    log.debug("connected to ssl socket")


  async def login(self):
    await self.open()
    android_id = self.credentials["gcm"]["androidId"]
    req = LoginRequest()
    req.adaptive_heartbeat = False
    req.auth_service = 2
    req.auth_token = self.credentials["gcm"]["securityToken"]
    req.id = "chrome-63.0.3234.0"
    req.domain = "mcs.android.com"
    req.device_id = "android-%x" % int(android_id)
    req.network_type = 1
    req.resource = android_id
    req.user = android_id
    req.use_rmq2 = True
    req.setting.add(name="new_vc", value="1")
    req.received_persistent_id.extend(self.persistent_ids)
    await self.send(req)
    login_response = await self.recv(first=True)
    log.info(f'Received login response:\n{login_response}')
    return login_response


  def reset(self):
    now = time.time()
    time_since_last_reset = now - self.last_reset
    if (time_since_last_reset < self.MIN_RESET_INTERVAL_SECS):
      log.debug(f"{time_since_last_reset}s since last reset attempt.")
      time.sleep(self.MIN_RESET_INTERVAL_SECS - time_since_last_reset)
    self.last_reset = now
    log.debug("Reestablishing connection")
    self.close_socket()
    self.login()


  def handle_data_message(self, p, callback, obj):
    import http_ece
    import cryptography.hazmat.primitives.serialization as serialization
    from cryptography.hazmat.backends import default_backend
    load_der_private_key = serialization.load_der_private_key

    crypto_key = self.app_data_by_key(p, "crypto-key")[3:]  # strip dh=
    salt = self.app_data_by_key(p, "encryption")[5:]  # strip salt=
    crypto_key = urlsafe_b64decode(crypto_key.encode("ascii"))
    salt = urlsafe_b64decode(salt.encode("ascii"))
    der_data = self.credentials["keys"]["private"]
    der_data = urlsafe_b64decode(der_data.encode("ascii") + b"========")
    secret = self.credentials["keys"]["secret"]
    secret = urlsafe_b64decode(secret.encode("ascii") + b"========")
    privkey = load_der_private_key(
        der_data, password=None, backend=default_backend()
    )
    decrypted = http_ece.decrypt(
        p.raw_data, salt=salt,
        private_key=privkey, dh=crypto_key,
        version="aesgcm",
        auth_secret=secret
    )
    log.info(f'Received data message {p.persistent_id}: {decrypted}')
    callback(obj, json.loads(decrypted.decode("utf-8")), p)
    return p.persistent_id


  async def handle_ping(self, p):
    log.debug(f'Responding to ping: Stream ID: {p.stream_id}, Last: {p.last_stream_id_received}, Status: {p.status}')
    req = HeartbeatAck()
    req.stream_id = p.stream_id + 1
    req.last_stream_id_received = p.stream_id
    req.status = p.status
    await self.send(req)


  async def status_check(self, term):
    await sleep(term)
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()


  async def listen(self, callback, term, obj=None):
    """
    listens for push notifications

    callback(obj, notification, data_message): called on notifications
    obj: optional arbitrary value passed to callback
    """
    login_resp = await self.login()
    print (login_resp)
    # create_task(self.status_check(term))
    # while True:
    #   data = await self.recv()
    #   if isinstance(data, DataMessageStanza):
    #     print ('DataMessageStanza')
    #     # id = self.handle_data_message(data, callback, obj)
    #     # self.persistent_ids.append(id)
    #   elif isinstance(data, HeartbeatPing):
    #     print ('HeartbeatPing')
    #     await self.handle_ping(data)
    #   elif data is None or isinstance(data, Close):
    #     return
    #   else:
    #     log.debug(f'Unexpected message type {type(data)}.')
