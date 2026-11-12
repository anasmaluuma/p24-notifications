PUBLISH notifications:user42 "Hello"
PSUBSCRIBE notifications:*
XADD history:user42 MAXLEN ~ 50 * type "evenement" msg "Reunion 14h" source "agenda"
XREVRANGE history:user42 + - COUNT 10
XRANGE history:user42 1794389125081 +
