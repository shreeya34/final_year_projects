def get_usage_data(report_id, time_range_start, time_range_end):

    query = '''

        from(bucket: "amazon")
                |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                |> filter(fn: (r) => r["_measurement"] == "coindesk")
                |> filter(fn: (r) => r["_field"] == "price")
                |> filter(fn: (r) => r["code"] == "EUR")
                |> filter(fn: (r) => r["crypto"] == "bitcoin")
                |> filter(fn: (r) => r["description"] == "Euro")
                |> filter(fn: (r) => r["symbol"] == "&euro;")
                |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
                |> yield(name: "mean")
        '''

    parameters = {
        "_bucket": amazon,
        "_time_range_start": time_range_start,
        "_time_range_end": time_range_end,
        "_report_id": str(report_id),
        "_measurement": coindesk_measurement,
    }

    fluxTables = client.query_api().query(query, org="grepsr", params=parameters)

    result = []

    for table in fluxTables:
        for row in table:
            result.append(row.values)

    return result