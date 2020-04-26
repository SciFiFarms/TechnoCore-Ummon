from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from inventorytracker.consumers import MqttConsumer

application = ProtocolTypeRouter({
  'channel': ChannelNameRouter(
    {
      "mqtt": MqttConsumer
    }
  )
})
