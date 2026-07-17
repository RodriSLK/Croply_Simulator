from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_crear_tablas_iniciales"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parcelas_simuladas",
        sa.Column("parcela_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("latitud", sa.Float(), nullable=False),
        sa.Column("longitud", sa.Float(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("creada_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "controladores_simulados",
        sa.Column("controlador_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column(
            "parcela_id",
            sa.Integer(),
            sa.ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ip_controlador", sa.String(length=45), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default=sa.text("'TRANSMITIENDO'")),
    )

    op.create_table(
        "sensores_simulados",
        sa.Column("sensor_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column(
            "controlador_id",
            sa.Integer(),
            sa.ForeignKey("controladores_simulados.controlador_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parcela_id",
            sa.Integer(),
            sa.ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("ip_sensor", sa.String(length=45), nullable=True),
        sa.Column("ultimo_valor", sa.Float(), nullable=True),
        sa.Column("fecha_ultima_lectura", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vwc_actual", sa.Float(), nullable=True),
        sa.Column("kc", sa.Float(), nullable=True, server_default=sa.text("0.4")),
        sa.Column("profundidad_radicular", sa.Float(), nullable=True, server_default=sa.text("0.4")),
        sa.Column("ph_base", sa.Float(), nullable=True, server_default=sa.text("6.5")),
    )

    op.create_table(
        "lecturas_simuladas",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "sensor_id",
            sa.Integer(),
            sa.ForeignKey("sensores_simulados.sensor_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parcela_id",
            sa.Integer(),
            sa.ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo_sensor", sa.String(length=30), nullable=False),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("unidad", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "alertas_simuladas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "parcela_id",
            sa.Integer(),
            sa.ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("valor_disparador", sa.Float(), nullable=False),
        sa.Column("resuelta", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "eventos_manuales_pendientes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "parcela_id",
            sa.Integer(),
            sa.ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo_evento", sa.String(length=30), nullable=False),
        sa.Column("parametros", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("aplicado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_index("idx_parcelas_activa", "parcelas_simuladas", ["activa"])
    op.create_index("idx_sensores_parcela", "sensores_simulados", ["parcela_id"])
    op.create_index(
        "idx_eventos_pendientes",
        "eventos_manuales_pendientes",
        ["parcela_id", "aplicado"],
        unique=False,
        postgresql_where=sa.text("aplicado = false"),
    )
    op.create_index(
        "idx_alertas_activas",
        "alertas_simuladas",
        ["parcela_id", "resuelta"],
        unique=False,
        postgresql_where=sa.text("resuelta = false"),
    )
    op.execute('CREATE INDEX idx_lecturas_sensor_timestamp ON lecturas_simuladas (sensor_id, "timestamp" DESC)')


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_lecturas_sensor_timestamp')
    op.drop_index("idx_alertas_activas", table_name="alertas_simuladas")
    op.drop_index("idx_eventos_pendientes", table_name="eventos_manuales_pendientes")
    op.drop_index("idx_sensores_parcela", table_name="sensores_simulados")
    op.drop_index("idx_parcelas_activa", table_name="parcelas_simuladas")
    op.drop_table("eventos_manuales_pendientes")
    op.drop_table("alertas_simuladas")
    op.drop_table("lecturas_simuladas")
    op.drop_table("sensores_simulados")
    op.drop_table("controladores_simulados")
    op.drop_table("parcelas_simuladas")