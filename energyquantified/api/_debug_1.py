# eq = EnergyQuantified(api_key='...')



# filters = [
#     CurveFilter().set_areas('DE', 'FR').set_commodities('Power'),
#     CurveFilter().set_areas('DE', 'FR').set_commodities('Power'),
#     CurveFilter().set_areas('DE', 'FR').set_commodities('Power'),
# ]

# filter_obj = (
#     CurveEventFilters()
#         .set_filter(filters)
#         .set_last_id(LAST_ID)
# )

# ws.subscribe(filter_obj, set_last_id=True)

# for type, obj in ws.get_next():
#     if type == EventType.TIMEOUT:
#         check_if_abort()
#     if type == EventType.MSG:
#         print(obj)
#     if type == EventType.CURVE_EVENT:
#         obj.load_data()
#     if type == EventType.FILTERS:
#         # subscribe() returned
#         pass


# # ----


# subscribe_failed = False

# def on_curves_subscribed(response):
#     if response.ok:
#         log.info("Subscribe OK")
#     else:
#         log.error("Failed to subscribe %s", response.msg)
#         subscribe_failed = True

# def on_remit_subscribed(response):
#     if response.ok:
#         log.info("Subscribe OK")
#     else:
#         log.error("Failed to subscribe %s", response.msg)
#         subscribe_failed = True


# class EnergyQuantifiedWS:

#     def __init__(self, last_id_file=None):
#         self._last_id

#     @property
#     def last_id(self):
#         return self._last_id


# eq = EnergyQuantified(api_key='...')
# ws = eq.events.connect(last_id_file='...')

# ws.subscribe_curve_events(
#     last_id='keep', # Keep last ID from WS if avail, 
#     filters=[
#         CurveFilter(curves=[]),
#         SearchFilter(areas=[], commodities=[]),
#     ],
#     callback=on_curves_subscribed
# )

# ws.subscribe_remit_events(
#     last_id=None,
#     filters=[
#         RemitFilter(areas=[], fuel_type=[])
#     ],
#     callback=on_remit_subscribed
# )



# class SearchFilter:

#     __init__(self, areas=None, commodities=None):
#         if areas:
#             self.set_areas(areas)
#         if commodities:
#             self.set_commodities(commodities)



# for type, obj in ws.get_next(timeout=5):
#     if type == EventType.TIMEOUT:
#         if response_failed:
#             # something went wrong, abort, log whatever
#             check_if_abort()
#     if type == EventType.CONNECTION_EVENT:
#         handle_errors()
#     if type == EventType.CURVE_EVENT:
#         obj.load_data()
#     if type == EventType.REMIT_EVENT:
#         remit_message = obj
#         # ...