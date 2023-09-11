.. code-block:: python
    eq.events.connect()

    filters = [...]

    def on_subscribe(response: CurvesSubscribeResponse):
        if response.success:
            print(
                f"Subscribed with filters: {response.data.filters}"
                f"{('from id:',response.data.last_id) if response.data.last_id is not None else ''}"
            )
        else:
            print(
                f"Failed to subscribe: {response.errors}, "
                f"retrying"
            )
            eq.events.subscribe_curve_events(
                filters=filters,
                callback=on_subscribe,
                timeout=30
            )

    eq.events.subscribe_curve_events(
        filters=[...],
        callback=on_subscribe,
        timeout=30,
    )

    def on_curve_filters(response: CurvesFiltersResponse):
        if response.success:
            print(f"Active curve filters: {response.data.filters}")
        else:
            print(
                f"Failed to get filters: {response.errors}, "
                f"retrying"
            )
            eq.events.get_curve_filters(callback=on_curve_filters, timeout=30)

    # Check active filters
    eq.events.get_curve_filters(callback=on_curve_filters, timeout=30)

    # We want to change filters after the first hour
    filters_2_sent = False
    filters_2_active = False
    filters_2 = [...]

    # Might be subscribed, might not. Let's start iterating regardless.
    for event in eq.events.get_next(timeout=10):
        print(event)

        if not filters_2_sent and datetime.now() > dt_start + timedelta(hours=1):

            # We can either reuse 'on_subscribe', or create a new one if we want
            # some custom stuff like setting filters_2_active to True, or sending
            # a get_filters request after a success response (just to be sure?)
            if reuse:
                eq.events.subscribe_curve_events(filters=filters_2, callback=on_subscribe, timeout=30)
                # Set bool before response since auto retry
                filters_2_sent = True
            else:
                def on_subscribe_2(response: CurvesSubscribeResponse):
                    if response.success:
                        print("subbed with filters2")
                        filters_2_active = True

                        # Let's also ask the server for the active filters to be sure
                        eq.events.get_curve_filters(callback=on_curve_filters, timeout=30)
                    else:
                        print(
                            f"failed to sub with filters2: {response.errors}, "
                            f"retrying"
                        )
                        eq.events.subscribe_curve_events(filters=filters_2, callback=on_subscribe_2, timeout=30)

                eq.events.subscribe_curve_events(filters=filters_2, callback=on_subscribe, timeout=30)
                # Set bool before response since auto retry
                filters_2_sent = True

            # Can't ask for filters after subscribing, if subscribe() fails
            # on the 1st try, and get_filters does not, we will get the old filters.
            # If both fail, it poses a raise condition that depends on the 'timeout'
            # of susbcribe and get_filters, and how long the code inside each
            # callback takes to execute. Consequently, we get_filters in the
            # custom subscribe callback


.. code-block:: python
    eq.events.connect()

    filters = [...]

    # Raises exception if fail
    response = eq.events.subscribe_curve_events(
        filters=[...],
        timeout=30,
    )
    print(
        f"Subscribed with filters: {response.filters}"
        f"{('from id:',response.data.last_id) if response.data.last_id is not None else ''}"
    )

    # Check active filters (exception raised if fail)
    active_filters = eq.events.get_curve_filters(timeout=30)
    print("Active filters confirmed by server:", active_filters)

    from datetime import datetime, timedelta
    dt_start = datetime.now()

    # We want to change filters after the first hour
    filter_2_active = False
    filters_2 = [...]

    # We know that we are subscribed and what filters is active. Start looping events.
    for event in eq.events.get_next(timeout=10):
        print(event)

        # Change filters after the first hour
        if not filters_2_active and datetime.now() > dt_start + timedelta(hours=1):
            # Raises exception if fail
            response = eq.events.subscribe_curve_events(filters=filters_2, timeout=30)
            print("subbed with the new filters: ", response.filters)
            print(".. from id:", response.last_id)
            filters_2_active = True

            # Let's also ask the server for the active filters to be sure
            # (raises exception if fail)
            currently_active_filters = eq.events.get_curve_filters(timeout=30)
            print("currently active filters:", currently_active_filters)