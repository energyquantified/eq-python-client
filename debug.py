from energyquantified import EnergyQuantified
from energyquantified.events.event_options import EventFilterOptions, EventCurveOptions
from energyquantified.events.events import EventType, CurveUpdateEvent, MessageType
import time
import json

def main():
    with open("api_key.json", "r") as f:
        data = json.load(f)
        key = data["key"]
        url = data["url"]
    eq = EnergyQuantified(api_key=key,
                          api_url=url,
                          last_id_file="last_id.json",
                          )
    #d = eq.metadata.curve("DE Wind Power Production MWh/h 15min Forecast")
    #print(f"curve: {d}")
    ws = eq.events.subscribe()
    
    timeout = 2
    for idx, (msg_type, event) in enumerate(ws.get_next(timeout=timeout)):
        print(f"({idx}) type: {msg_type}, msg: {event}")
        #ws._ws.close()
        if msg_type == MessageType.EVENT:
            #curve = event.curve
            #data=None
            assert isinstance(event, CurveUpdateEvent)
            data = event.load_data(eq)
            print(f"data: {data}")
            for val in data:
                print(f"val: {val}")
        if idx == 1:
            filter_1 = EventFilterOptions().set_areas("DE")#.set_event_types(EventType.DELETE)
            ws.set_filters(filter_1)
            ws.send_get_filters()
        if idx == 10:
            # new_filter = EventCurveOptions().set_curves("DE Wind Power Production MWh/h 15min Forecast")
            # #new_filter.set_event_types(EventType.DELETE)
            # print(f"f: {new_filter}")
            # print(f"f.todict: {new_filter.to_dict()}")
            # ws.set_filters(new_filter)
            # ws.get_filters()
            pass
        if idx == 15:
            #print("closing")
            #ws.close()
            pass
    time.sleep(1)
    # print()
    # print("Get filter..")
    # #filters = ws.get_filters()
    # ws.get_filters()
    # #print(f"Got filters: {filters}")
    # print()
    # print("Wait for events..")
    # events = []
    
    # timeout = 2
    # for idx, (msg_type, event) in enumerate(ws.get_next(timeout=timeout)):
    #     # TODO disconnect event

    #     # TODO load method for getting the changed data
    #     # ^event.load_event_data() or something
    #     # TODO ctrl+c dc event
    #     print(f"Got msg_type: {msg_type}")
    #     print(f"Got event: {event}")
    #     events.append(event)
    #     # if len(events) >= 2:
    #     #     ws.update_filter("")
    #     #ws.update_filter()
    #     if idx == 1:
    #         print(f"getting filters again, got: {ws.get_filters()}")
    #         print("changing filters")
    #         new_filter = EventCurveOptions().set_curves("DE Wind Power Production MWh/h 15min Forecast")
    #         ws.set_filters(new_filter)
    #         print(f"getting filters after change, got: {ws.get_filters()}")
    #     print()
        

if __name__ == "__main__":
    main()