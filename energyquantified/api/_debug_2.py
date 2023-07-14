# class Callbacks:

#   def __init__(self, callback, type='subscrive_curves', latest=True):
#     self.callback = callback
#     self.type = type
#     self.latest = latest

# def subscribe_curve_events(....):
#   """
#   last_id (str, None):
#     * If None, don't provide.
#     * If 'keep', reuse remembered last_id if we have it, otherwonse don't provide
#     * if '123455(?-1234)' provide this id
#   """
#   with lock.acquire():
#     for key, item in callbacks.items():
#       item.latest = False
#     callbacks['uuid_new'] = Callbacks(...)
#     clear_curve_events()
#     set_curve_events_active(False)



# callbacks = {
#   'uuid1': callback_func
# }

# curve_events_active = False

# on_ws_msg(msg):
#     if msg.curve_event:
#         if curve_events_active:
#             # process
#             pass
#     if msg.subscribe: # type = set_filters
#         callback = callbakcs[msg.uuid]
#         if callback:
#             if callback.latest and not msg.error:
#                 curve_events_active = True
#             callback.callback(to_response(msg))

        
  

#   msg.uuid not in callbacks -> ignore
#   msg.uuid in callbacks -> invoke callback, set curve_events_active = True


# class SubscribeResponse:

#     def __init__(self, ok, obj, errors):
#         self.ok = ok
#         self.obj = obj
#         self.errors = errors


# subscribe_failed = False

# def on_curves_subscribed(response: SubscribeResponse):
#     if response.ok:
#         filters = response.obj.filters 
#         last_id = response.obj.last_id  # None or "123456677-0"
#         log.info("Subscribe OK")
#     else:
#         errors = response.errors
#         log.error("Failed to subscribe %s", response.msg)
#         subscribe_failed = True