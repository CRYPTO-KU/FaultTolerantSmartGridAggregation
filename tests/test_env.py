import pytest_asyncio
import pytest
from time import time as now
from aggft.dc.http_masking import HTTPMaskingDC

@pytest.mark.asyncio
async def test_answer():
    dc = HTTPMaskingDC(
        6969,
        [],
        0,
        now(),
        10, 5, 5, 500
    )

    await dc.run()
