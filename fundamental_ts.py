import datetime
from timeseries.db import (
    select_query,
    InfluxDBClient,
    DB_NAME,
    DB_HOST,
    influx_res_to_dict,
)
import logging


class FundamentalTimeseries:
    def __init__(self, fmp):
        self._fmp = fmp

    async def market_cap(self, symbol):
        data = await self._fmp.get_historical_market_cap(symbol)
        res = []
        for datum in data:
            date = datetime.datetime.strptime(datum["date"], "%Y-%m-%d")
            res.append(
                {
                    "symbol": symbol,
                    "fundamental": "market_cap",
                    "timestamp": date,
                    "val": float(datum["marketCap"]),
                }
            )
        return res

    async def revenue_ttm(self, symbol):
        # 50 years, 4 quarters
        data = await self._fmp.get_income_statement(
            symbol, limit=50 * 4, period="quarter"
        )

        no_quarters = len(data)

        res = []
        for i in range(no_quarters):
            current = data[i]
            quarters = [current]

            if i + 1 < no_quarters:
                quarters.append(data[i + 1])
            if i + 2 < no_quarters:
                quarters.append(data[i + 2])
            if i + 3 < no_quarters:
                quarters.append(data[i + 3])

            date = datetime.datetime.strptime(current["date"], "%Y-%m-%d")
            res.append(
                {
                    "symbol": symbol,
                    "fundamental": "revenue_ttm",
                    "timestamp": date,
                    "val": sum([quarter["revenue"] for quarter in quarters]),
                }
            )
        return res

    async def get_fundamental_timeseries(self, symbol, fundamental):
        logging.info("getting fts %s %s", symbol, fundamental)
        return influx_res_to_dict(
            await select_query(
                f"SELECT * FROM fundamentals WHERE symbol='{symbol}' AND fundamental='{fundamental}' ORDER BY time DESC"
            )
        )

    async def store_fundamental_timeseries(self, data, symbol, fundamental):
        async with InfluxDBClient(db=DB_NAME, host=DB_HOST) as client:
            await client.create_database(db=DB_NAME)

            points = []
            for datum in data:
                points.append(
                    {
                        "time": datum["timestamp"],
                        "measurement": "fundamentals",
                        "tags": {
                            "symbol": symbol,
                            "fundamental": fundamental,
                        },
                        "fields": {"val": datum["val"]},
                    }
                )

            await client.write(points)

    async def price_to_sales_ttm(self, symbol):
        market_cap = await self.get_fundamental_timeseries(
            symbol, fundamental="market_cap"
        )
        revenue_ttm = await self.get_fundamental_timeseries(
            symbol, fundamental="revenue_ttm"
        )

        curr_quarter = 0

        res = []

        for mc in market_cap:
            if mc["timestamp"] > revenue_ttm[curr_quarter]["timestamp"]:
                res.append(
                    {
                        "symbol": symbol,
                        "fundamental": "price_to_sales_ttm",
                        "timestamp": datetime.datetime.fromtimestamp(
                            mc["timestamp"] / 10 ** 9
                        ),
                        "val": mc["val"] / revenue_ttm[curr_quarter]["val"],
                    }
                )
            else:
                curr_quarter += 1
                res.append(
                    {
                        "symbol": symbol,
                        "fundamental": "price_to_sales_ttm",
                        "timestamp": datetime.datetime.fromtimestamp(
                            mc["timestamp"] / 10 ** 9
                        ),
                        "val": mc["val"] / revenue_ttm[curr_quarter]["val"],
                    }
                )

        return res
