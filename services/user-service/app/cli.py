import asyncio
import getpass
import sys

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import AdminUserCreate
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

BOOTSTRAP_LOCK_KEY = 71824093615


async def create_first_admin(payload: AdminUserCreate) -> str:
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                await session.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_key)"),
                    {"lock_key": BOOTSTRAP_LOCK_KEY},
                )
                existing_admin = await session.scalar(
                    select(User.id).where(User.is_admin.is_(True)).limit(1)
                )
                if existing_admin is not None:
                    return "Já existe uma conta gerente; o bootstrap foi cancelado."

                session.add(
                    User(
                        username=payload.username,
                        email=str(payload.email),
                        hashed_password=get_password_hash(payload.password),
                        is_admin=True,
                    )
                )
            return "Primeiro gerente cadastrado com sucesso."
        except IntegrityError:
            return "Já existe uma conta com esse nome ou e-mail."
        except SQLAlchemyError:
            return "Não foi possível acessar o banco para cadastrar o gerente."


def main() -> int:
    if sys.argv[1:] != ["create-admin"]:
        print("Uso: python -m app.cli create-admin", file=sys.stderr)
        return 2
    if not sys.stdin.isatty():
        print("Execute este comando em um terminal interativo.", file=sys.stderr)
        return 2

    username = input("Nome de usuário: ").strip()
    email = input("E-mail: ").strip()
    password = getpass.getpass("Senha: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if password != confirmation:
        print("As senhas não coincidem.", file=sys.stderr)
        return 2

    try:
        payload = AdminUserCreate(
            username=username,
            email=email,
            password=password,
            is_admin=True,
        )
    except ValidationError as exc:
        for error in exc.errors(include_url=False):
            print(f"Dados inválidos: {error['msg']}", file=sys.stderr)
        return 2

    result = asyncio.run(create_first_admin(payload))
    print(result)
    return 0 if result.startswith("Primeiro gerente") else 1


if __name__ == "__main__":
    raise SystemExit(main())
