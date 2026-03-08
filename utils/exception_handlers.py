from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException

from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, \
    general_error_handler


def register_error_handlers(app):
    """
    注册全局处理异常：子类在前，父类在后；具体在前，抽象在后
    :param app:
    :return:
    """
    app.add_exception_handler(HTTPException, http_exception_handler) # 业务层
    app.add_exception_handler(IntegrityError, integrity_error_handler) # 数据完整性约束
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler) # 数据库
    app.add_exception_handler(Exception, general_error_handler)  # 其他错误，兜底