from __future__ import annotations
from datetime import datetime, date
from zoneinfo import available_timezones
from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Funcție auxiliară ─────────────────────────────────────────────────────

def validate_timezone(value: str) -> str:
    """
    Verifică că timezone-ul este un nume IANA valid.
    De exemplu: "Europe/Bucharest" ✓, "blablabla" ✗
    """
    if value not in available_timezones():
        raise ValueError(
            f"'{value}' nu este un timezone valid. "
            f"Exemple corecte: 'Europe/Bucharest', 'Europe/Moscow', 'Asia/Almaty'"
        )
    return value


# ─── Scheme pentru creare și actualizare utilizator ───────────────────────

class UserCreate(BaseModel):
    """Schemă pentru înregistrarea unui utilizator nou."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Numele de utilizator"
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Minim 8 caractere, o cifră, o literă"
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """Parola trebuie să conțină cel puțin o cifră și o literă."""
        are_cifra = any(c.isdigit() for c in value)
        are_litera = any(c.isalpha() for c in value)

        if not are_cifra:
            raise ValueError("Parola trebuie să conțină cel puțin o cifră")
        if not are_litera:
            raise ValueError("Parola trebuie să conțină cel puțin o literă")

        return value


class UserUpdate(BaseModel):
    """Schemă pentru PATCH /users/me — actualizarea profilului."""
    avatar_id: int | None = Field(
        None,
        ge=1,
        le=20,
        description="ID avatar între 1 și 20"
    )
    daily_goal_target: int | None = Field(
        None,
        description="Obiectivul zilnic: 3, 5, 10 sau 15 sarcini"
    )
    timezone: str | None = Field(
        None,
        description="Timezone IANA valid, ex: Europe/Bucharest"
    )

    @field_validator("daily_goal_target")
    @classmethod
    def valideaza_obiectiv_zilnic(cls, value: int | None) -> int | None:
        """Valorile permise pentru obiectivul zilnic: 3, 5, 10, 15."""
        if value is not None and value not in (3, 5, 10, 15):
            raise ValueError(
                "daily_goal_target trebuie să fie unul din: 3, 5, 10, 15"
            )
        return value

    @field_validator("timezone")
    @classmethod
    def valideaza_timezone(cls, value: str | None) -> str | None:
        """Verifică că timezone-ul este valid conform standardului IANA."""
        if value is not None:
            return validate_timezone(value)
        return value


# ─── Scheme pentru răspunsuri (ce trimitem clientului) ────────────────────

class UserPublic(BaseModel):
    """
    Date publice ale utilizatorului — fără parolă și câmpuri de serviciu.
    Folosit în răspunsurile API pentru a nu expune date sensibile.
    """
    id: int
    username: str
    email: str
    avatar_id: int
    elo_rating: float
    current_streak: int
    max_streak: int
    daily_goal_target: int
    timezone: str
    last_activity_date: date | None
    is_active: bool
    created_at: datetime

    # Permite crearea din obiecte SQLAlchemy
    model_config = {"from_attributes": True}


class UserStats(BaseModel):
    """
    Statistici utilizator — calculate în serviciu, nu stocate în DB.
    Returnate în răspunsul GET /users/me.
    """
    total_solved: int
    total_correct: int
    accuracy_percent: float
    favorite_category: str | None


class UserProfile(UserPublic):
    """
    Profil extins pentru GET /users/me.
    Moștenește toate câmpurile din UserPublic și adaugă
    câmpuri calculate care nu există în baza de date.
    """
    rank: str = "Bronze"
    stats: UserStats | None = None


# Pydantic necesită rebuild deoarece UserStats este definit după UserProfile.
UserProfile.model_rebuild()
