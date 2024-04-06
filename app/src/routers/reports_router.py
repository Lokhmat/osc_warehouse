import logging
import typing

from io import BytesIO

import pandas as pd

from fastapi import APIRouter, Depends, Response

from ..models import helpers
from ..models import users
from ..models import reports
from ..utils import crypto

EXCEL_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

reports_router = APIRouter(tags=["reports"])


@reports_router.post(
    "/reports/file",
    responses={
        200: {"content": {EXCEL_CONTENT_TYPE: {}}},
        **helpers.UNATHORIZED_RESPONSE,
    },
)
async def get_reports_file(
    request: reports.ReportRequest,
    _: typing.Annotated[users.InternalUser, Depends(crypto.authorize_admin_with_token)],
):
    report = reports.report_generator.prepare_report(request.interval)
    df = pd.DataFrame(report.items, columns=report.header)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type=EXCEL_CONTENT_TYPE,
    )


@reports_router.post(
    "/reports", response_model=reports.Report, responses=helpers.UNATHORIZED_RESPONSE
)
async def get_reports_by_interval(
    request: reports.ReportRequest,
    _: typing.Annotated[users.InternalUser, Depends(crypto.authorize_admin_with_token)],
):
    return reports.report_generator.prepare_report(request.interval)
