import json
import datetime
from random import shuffle
from hashlib import md5

from ariadne import (MutationType, QueryType, SubscriptionType, load_schema_from_path, make_executable_schema)
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from broadcaster import Broadcast
from starlette.applications import Starlette

broadcast = Broadcast("redis://localhost:6379")
mutation = MutationType()
subscription = SubscriptionType()
query = QueryType()

type_defs = """
  type Query {
    _unused: Boolean
    history: History
  }

  type Message {
    sender: String
    message: String
    timestamp: String
  }

  type Mutation {
    send(sender: String!, message: String!): Boolean
  }
  
  type History {
    history: [Message]
  }

  type Subscription {
    message: Message
  }
"""

history = [
    {
        "sender": "System",
        "message": f"Chat started",
        "timestamp": str(datetime.datetime.now()),
    },
]

@query.field("history")
def resolve_history(*_):
    return history[-10:]


@subscription.source("message")
async def source_message(_, info):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            yield json.loads(event.message)


@mutation.field("send")
async def resolve_send(*_, **message):
    message["timestamp"] = datetime.datetime.now()
    history.append(message)
    await broadcast.publish(channel="chatroom", message=json.dumps(message))
    return True


schema = make_executable_schema(type_defs, query, mutation, subscription)
graphql = GraphQL(
    schema=schema,
    debug=True,
    websocket_handler=GraphQLTransportWSHandler(),
)

# Setup Starlette ASGI app with events to start and stop Broadcaster
app = Starlette(
    debug=True,
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)

# Mount ASGI app to handle GET and POST methods
app.mount("/graphql/", graphql)

# Mount ASGI app to handle websocket connections
app.add_websocket_route("/graphql/", graphql)
