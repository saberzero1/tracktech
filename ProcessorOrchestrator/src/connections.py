"""File which contains dicts with the currently open websocket connections"""

processors = dict()
"""Dictionary which matches processor id to the corresponding websocket

type: Dict[str, ProcessorSocket]
"""

clients = dict()
"""Dictionary which matches client id to the corresponding websocket

type: Dict[str, ClientSocket]
"""
