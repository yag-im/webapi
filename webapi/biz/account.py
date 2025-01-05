from webapi.biz.misc import log_input_output
from webapi.dto.account import UpdateUserRequestDTO
from webapi.models.account import UserDAO
from webapi.sqldb import sqldb


def get_user(user_id: int) -> UserDAO:
    return UserDAO.query.filter_by(id=user_id).first()


@log_input_output
def update_user(user_id: int, user: UpdateUserRequestDTO) -> None:
    sqldb.session.query(UserDAO).filter(UserDAO.id == user_id).update(
        {
            UserDAO.email: user.email,
            UserDAO.name: user.name,
            UserDAO.tz: user.tz,
            UserDAO.apps_lib: user.apps_lib,
            UserDAO.dob: user.dob,
        }
    )
    sqldb.session.commit()
